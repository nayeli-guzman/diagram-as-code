import os
import json
import tempfile
import subprocess

from eralchemy import render_er

def lambda_handler(event, context):
    os.environ["PATH"] += ":/opt/bin"  # Para asegurar acceso a dot

    try:
        body = json.loads(event["body"])
        dsl_text = body.get("dsl")

        if not dsl_text:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No se envió texto DSL"}),
                "headers": {"Content-Type": "application/json"}
            }

        # Crear archivo temporal con DSL
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.er', delete=False) as dsl_file:
            dsl_file.write(dsl_text)
            dsl_path = dsl_file.name

        # Crear archivo de salida
        out_path = dsl_path.replace('.er', '.png')

        # Generar imagen con ERAlchemy
        render_er(dsl_path, out_path)

        # Leer la imagen generada y devolver en base64
        with open(out_path, "rb") as img_file:
            img_base64 = img_file.read()

        return {
            "statusCode": 200,
            "body": img_base64.decode("latin1"),  # se recomienda usar base64 si es binario
            "isBase64Encoded": True,
            "headers": {
                "Content-Type": "image/png"
            }
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {"Content-Type": "application/json"}
        }
