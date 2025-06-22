from fastapi import FastAPI
import boto3, json, os
from eralchemy import render_er
import tempfile

bucket_name = "er-bucket"
output_path = "/tmp/diagrama_er.png"

def lambda_handler(event, context):
    print(event)
    body = json.loads(event["body"])
    dsl = body.get("dsl")  # Código ER en formato DSL
    user_id = body.get("user_id")

    if not dsl or not user_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Falta dsl o user_id'}),
            'headers': {'Content-Type': 'application/json'}
        }

    try:
        # Escribir DSL a archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dsl", mode='w') as dsl_file:
            dsl_file.write(dsl)
            dsl_path = dsl_file.name

        # Renderizar como imagen PNG
        render_er(dsl_path, output_path)

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
        # Detallar el error
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Ocurrió un error: {str(e)}'}),
            'headers': {'Content-Type': 'application/json'}
        }
