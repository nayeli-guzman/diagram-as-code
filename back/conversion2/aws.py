import boto3
import json
import os
import re
import tempfile
import shutil
from eralchemy import render_er
from eralchemy.cst import GRAPHVIZ_EXECUTABLE
from subprocess import run

# Configuración
bucket_name = "e-rbucket"
output_path = "/tmp/diagrama_er.png"
user_validar = "diagram-usuarios-dev-validar"

def is_valid_sqlalchemy_url(dsl):
    """Verifica si el DSL es una URL SQLAlchemy válida"""
    patterns = [
        r'^sqlite:///',
        r'^postgresql://',
        r'^mysql://',
        r'^oracle://',
        r'^mssql://'
    ]
    return any(re.match(pattern, dsl.strip()) for pattern in patterns)

def generate_diagram(dsl_content, output_path):
    """Genera el diagrama ER usando diferentes métodos con fallback"""
    methods = [
        lambda: render_er(dsl_content, output_path),
        lambda: generate_with_graphviz(dsl_content, output_path)
    ]
    
    for method in methods:
        try:
            method()
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return True
        except Exception as e:
            print(f"Método falló: {str(e)}")
            continue
    
    return False

def generate_with_graphviz(dsl_content, output_path):
    """Genera el diagrama usando Graphviz directamente"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.dot', delete=False, dir='/tmp') as dot_file:
        dot_path = dot_file.name
        render_er(dsl_content, dot_path)
    
    cmd = [
        GRAPHVIZ_EXECUTABLE,
        '-Tpng',
        '-o', output_path,
        dot_path
    ]
    
    result = run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Graphviz falló: {result.stderr}")

def lambda_handler(event, context):
    try:
        print("Inicio de la función Lambda")
        print(f"Contenido de /tmp al inicio: {os.listdir('/tmp')}")
        
        # Parsear entrada
        body = json.loads(event['body'])
        token = event['headers']['Authorization']
        tenant_id = body['tenant_id']
        user_id = body['user_id']
        dsl_content = body["dsl"].replace("\\n", "\n").replace("\\t", "\t").strip()
        
        print(f"DSL recibido:\n{dsl_content}")
        
        # Validar token (mantener tu lógica existente)
        lambda_client = boto3.client('lambda')
        payload = {"token": token, "tenant_id": tenant_id}
        invoke_response = lambda_client.invoke(
            FunctionName=user_validar,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        response = json.loads(invoke_response['Payload'].read())
        
        if response['statusCode'] == 403:
            return {
                'statusCode': 403,
                'body': json.dumps({'status': 'Forbidden - Acceso No Autorizado'}),
                'headers': {'Content-Type': 'application/json'}
            }
        
        # Preparar entorno
        os.makedirs("/tmp", exist_ok=True)
        if os.path.exists(output_path):
            os.remove(output_path)
        
        # Procesar DSL
        if is_valid_sqlalchemy_url(dsl_content):
            print("Procesando como URL SQLAlchemy")
            input_source = dsl_content
        else:
            print("Procesando como DSL estándar")
            with tempfile.NamedTemporaryFile(mode='w', suffix='.er', delete=False, dir='/tmp') as tmp_file:
                tmp_file.write(dsl_content)
                input_source = tmp_file.name
            print(f"Archivo temporal creado en: {input_source}")
        
        # Generar diagrama
        if not generate_diagram(input_source, output_path):
            raise RuntimeError("Todos los métodos para generar el diagrama fallaron")
        
        print(f"Diagrama generado en {output_path} (Tamaño: {os.path.getsize(output_path)} bytes)")
        
        # Subir a S3
        s3 = boto3.client("s3")
        s3_key = f"er-diagrama-{user_id}.png"
        s3.upload_file(output_path, bucket_name, s3_key)
        image_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'imageUrl': image_url,
                'message': 'Diagrama generado exitosamente'
            }),
            'headers': {'Content-Type': 'application/json'}
        }
        
    except Exception as e:
        print(f"Error completo: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Error al generar el diagrama: {str(e)}',
                'suggestion': 'Verifique: 1) El formato del DSL 2) Que Graphviz esté instalado 3) Los permisos en /tmp'
            }),
            'headers': {'Content-Type': 'application/json'}
        }
    finally:
        # Limpieza
        if 'input_source' in locals() and os.path.exists(input_source) and input_source != dsl_content:
            os.remove(input_source)
        print(f"Contenido de /tmp al final: {os.listdir('/tmp')}")