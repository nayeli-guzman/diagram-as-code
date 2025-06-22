import os
import json
import tempfile
import boto3
import base64
from eralchemy import render_er

def lambda_handler(event, context):
    os.environ["PATH"] += ":/opt/bin"
    s3 = boto3.client("s3")
    bucket_name = "e-rbucket"

    try:
        body = json.loads(event["body"])
        dsl_text = body.get("dsl")

        if not dsl_text:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No se envió texto DSL"}),
                "headers": {"Content-Type": "application/json"}
            }

        # Crear archivo temporal DSL
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.er', delete=False) as dsl_file:
            dsl_file.write(dsl_text)
            dsl_path = dsl_file.name

        # Generar imagen
        out_path = dsl_path.replace('.er', '.png')
        render_er(dsl_path, out_path)

        # Nombre único en S3
        filename = f"erd_{context.aws_request_id}.png"

        # Subir imagen a S3
        with open(out_path, "rb") as f:
            s3.upload_fileobj(f, bucket_name, filename, ExtraArgs={"ACL": "public-read", "ContentType": "image/png"})

        # Construir URL pública
        file_url = f"https://{bucket_name}.s3.amazonaws.com/{filename}"

        return {
            "statusCode": 200,
            "body": json.dumps({"url": file_url}),
            "headers": {"Content-Type": "application/json"}
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {"Content-Type": "application/json"}
        }
