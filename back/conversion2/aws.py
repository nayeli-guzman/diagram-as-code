import boto3, json, os
from eralchemy import render_er
import tempfile

bucket_name = "e-rbucket"
output_path = "/tmp/diagrama_er.png"

# Nombre de la función Lambda de validación
user_validar = f"diagram-usuarios-dev-validar"

def lambda_handler(event, context):
    print(event)
    
    # Entrada (json)
    body = json.loads(event['body'])
    
    # Extraer token desde el header de autorización
    token = event['headers']['Authorization']
    tenant_id = body['tenant_id']
    user_id = body['user_id']

    # Proteger el Lambda: llamar a la función de validación del token
    lambda_client = boto3.client('lambda')
    payload = {
        "token": token,
        "tenant_id": tenant_id
    }
    
    # Invocar la función de validación del token
    invoke_response = lambda_client.invoke(
        FunctionName=user_validar,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    
    # Leer la respuesta de la función de validación
    response = json.loads(invoke_response['Payload'].read())
    print(response)
    
    # Si la respuesta es 403, significa que el acceso no está autorizado
    if response['statusCode'] == 403:
        return {
            'statusCode': 403,
            'body': json.dumps({'status': 'Forbidden - Acceso No Autorizado'}),
            'headers': {'Content-Type': 'application/json'}
        }
    
    # Si el token es válido, continuar con la creación del diagrama
    if not body.get("dsl") or not user_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Falta dsl o user_id'}),
            'headers': {'Content-Type': 'application/json'}
        }

    try:
        # Verificar si /tmp existe y es escribible
        if not os.path.exists('/tmp'):
            os.makedirs('/tmp')  # Crear directorio si no existe

        if not os.access('/tmp', os.W_OK):
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'El directorio /tmp no es escribible'}),
                'headers': {'Content-Type': 'application/json'}
            }

        # Escribir DSL a archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dsl", mode='w') as dsl_file:
            dsl_file.write(body["dsl"])
            dsl_path = dsl_file.name
            print(f"DSL Path creado: {dsl_path}")  # Verifica la ruta del archivo temporal

        # Verificar si el archivo temporal se ha creado correctamente
        if not os.path.exists(dsl_path):
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f"El archivo DSL no se creó correctamente: {dsl_path}"}),
                'headers': {'Content-Type': 'application/json'}
            }

        # Renderizar como imagen PNG
        print(f"Generando diagrama ER en {output_path}")
        render_er(dsl_path, output_path)

        # Verificar si la imagen se generó correctamente
        if not os.path.exists(output_path):
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f"El archivo de imagen no se generó correctamente: {output_path}"}),
                'headers': {'Content-Type': 'application/json'}
            }

        # Subir a S3
        s3 = boto3.client("s3")
        s3_key = f"er-diagrama-{user_id}.png"
        print(f"Subiendo el archivo {output_path} a S3 con la clave {s3_key}")
        s3.upload_file(output_path, bucket_name, s3_key)

        image_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"

        return {
            'statusCode': 200,
            'body': json.dumps({'imageUrl': image_url}),
            'headers': {'Content-Type': 'application/json'}
        }

    except Exception as e:
        # Detallar el error
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Ocurrió un error: {str(e)}'}),
            'headers': {'Content-Type': 'application/json'}
        }
