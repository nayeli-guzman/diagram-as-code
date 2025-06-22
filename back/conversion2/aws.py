import boto3, json, os
from eralchemy import render_er
import tempfile
import re
import shutil

bucket_name = "e-rbucket"
output_path = "/tmp/diagrama_er.png"
user_validar = f"diagram-usuarios-dev-validar"

def is_valid_sqlalchemy_url(dsl):
    patterns = [
        r'^sqlite:///',
        r'^postgresql://',
        r'^mysql://',
        r'^oracle://',
        r'^mssql://'
    ]
    return any(re.match(pattern, dsl.strip()) for pattern in patterns)

def lambda_handler(event, context):
    try:
        # [Sección de validación del token - mantener igual]
        
        # Preprocesar el DSL
        dsl_cleaned = body["dsl"].replace("\\n", "\n").replace("\\t", "\t").strip()
        print(f"DSL recibido:\n{dsl_cleaned}")

        # Asegurar que el directorio /tmp existe
        os.makedirs("/tmp", exist_ok=True)

        # Limpiar archivos previos
        if os.path.exists(output_path):
            os.remove(output_path)

        # Crear archivo temporal con extensión .er (requerido por eralchemy)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.er', delete=False, dir='/tmp') as tmp_file:
            tmp_file.write(dsl_cleaned)
            tmp_path = tmp_file.name
            print(f"Archivo temporal creado en: {tmp_path}")

        # Verificar contenido del archivo
        with open(tmp_path, 'r') as f:
            content = f.read()
            if not content.strip():
                raise ValueError("El archivo DSL está vacío")

        # 1. Intento principal con render_er
        try:
            print("Intentando renderizar con eralchemy...")
            render_er(tmp_path, output_path)
            
            if not os.path.exists(output_path):
                raise RuntimeError("Render_er no generó el archivo de salida")
                
            print(f"Diagrama generado correctamente en {output_path}")

        except Exception as e:
            print(f"Error con render_er: {str(e)}")
            # 2. Intento alternativo con system_graphviz
            try:
                from eralchemy.cst import GRAPHVIZ_EXECUTABLE
                from subprocess import run
                
                dot_path = tmp_path + '.dot'
                cmd = [
                    GRAPHVIZ_EXECUTABLE,
                    '-Tpng',
                    '-o', output_path,
                    dot_path
                ]
                
                # Generar archivo .dot primero
                from eralchemy import render_er
                render_er(tmp_path, dot_path)
                
                print(f"Ejecutando: {' '.join(cmd)}")
                result = run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    raise RuntimeError(f"Graphviz falló: {result.stderr}")
                    
            except Exception as fallback_e:
                print(f"Error en método alternativo: {str(fallback_e)}")
                raise RuntimeError(f"Todos los métodos fallaron: {str(e)} y {str(fallback_e)}")

        # Verificar que la imagen se generó
        if not os.path.exists(output_path):
            raise RuntimeError("No se pudo generar el archivo de imagen después de todos los intentos")
        
        # [Resto del código para subir a S3 - mantener igual]

    except Exception as e:
        print(f"Error completo: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Error al generar el diagrama: {str(e)}',
                'suggestion': 'Verifique que el DSL tenga el formato correcto y que Graphviz esté instalado correctamente'
            }),
            'headers': {'Content-Type': 'application/json'}
        }
    finally:
        # Limpieza de archivos temporales
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)