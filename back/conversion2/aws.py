import boto3, json, os
from eralchemy import render_er
import tempfile
import re

bucket_name = "e-rbucket"
output_path = "/tmp/diagrama_er.png"
user_validar = f"diagram-usuarios-dev-validar"

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

def lambda_handler(event, context):
    print(event)
    
    try:
        body = json.loads(event['body'])
        token = event['headers']['Authorization']
        tenant_id = body['tenant_id']
        user_id = body['user_id']
        
        # Validación del token (tu código existente)
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
        
        if not body.get("dsl") or not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Falta dsl o user_id'}),
                'headers': {'Content-Type': 'application/json'}
            }

        # Preprocesar el DSL
        dsl_cleaned = body["dsl"].replace("\\n", "\n").replace("\\t", "\t").strip()
        print(f"DSL limpio:\n{dsl_cleaned}")

        # Verificar si es una URL SQLAlchemy válida
        is_sqlalchemy = is_valid_sqlalchemy_url(dsl_cleaned)
        
        # Si no es una URL SQLAlchemy, escribir a archivo temporal
        if not is_sqlalchemy:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".er", mode='w') as dsl_file:
                dsl_file.write(dsl_cleaned)
                dsl_path = dsl_file.name
                print(f"Archivo DSL creado en: {dsl_path}")
            
            # Verificar que el archivo tiene contenido válido
            with open(dsl_path, 'r') as f:
                content = f.read()
                if not content.strip():
                    raise ValueError("El archivo DSL está vacío")
        else:
            dsl_path = dsl_cleaned

        # Renderizar el diagrama
        try:
            render_er(dsl_path, output_path)
            print(f"Diagrama generado en {output_path}")
            
            # Verificar que la imagen se creó
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise ValueError("No se generó el archivo de imagen")
                
        except Exception as e:
            print(f"Error al renderizar: {str(e)}")
            # Intento alternativo con formato diferente
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".dot", mode='w') as dot_file:
                    dot_file.write(dsl_cleaned)
                    dot_path = dot_file.name
                
                render_er(dot_path, output_path)
            except Exception as fallback_e:
                raise ValueError(f"Error principal y alternativo: {str(e)} | {str(fallback_e)}")

        # Subir a S3
        s3 = boto3.client("s3")
        s3_key = f"er-diagrama-{user_id}.png"
        s3.upload_file(output_path, bucket_name, s3_key)
        image_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"

        return {
            'statusCode': 200,
            'body': json.dumps({'imageUrl': image_url}),
            'headers': {'Content-Type': 'application/json'}
        }

    except Exception as e:
        print(f"Error completo: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error al procesar el DSL: {str(e)}'}),
            'headers': {'Content-Type': 'application/json'}
        }