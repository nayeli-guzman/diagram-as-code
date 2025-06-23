import boto3, json, os
from eralchemy import render_er
import tempfile

bucket_name = "mi-bucket-diagrams"
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

        # Preprocesar el DSL: Limpiar caracteres de escape y saltos de línea
        dsl_cleaned = body["dsl"].replace("\\n", "\n").replace("\\t", "\t").strip()
        
        # Agregar depuración para ver el DSL limpio
        print(f"DSL limpio:\n{dsl_cleaned}")  # Verifica si el DSL se limpió correctamente

        # Escribir DSL limpio a archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dsl", mode='w') as dsl_file:
            dsl_file.write(dsl_cleaned)
            dsl_path = dsl_file.name
            print(f"DSL Path creado: {dsl_path}")  # Verifica la ruta del archivo temporal

        # Verificar si el archivo temporal se ha creado correctamente
        if not os.path.exists(dsl_path):
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f"El archivo DSL no se creó correctamente: {dsl_path}"}),
                'headers': {'Content-Type': 'application/json'}
            }

        # Verificar contenido del archivo .dsl
        with open(dsl_path, 'r') as file:
            dsl_content = file.read()
            print(f"Contenido del archivo .dsl:\n{dsl_content}")

        # Intentar importar graphviz para verificar que está disponible
        try:
            import graphviz
            print("Graphviz importado correctamente")
        except Exception as e:
            print(f"Error al importar Graphviz: {str(e)}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f"Error al importar Graphviz: {str(e)}"}),
                'headers': {'Content-Type': 'application/json'}
            }

        # Renderizar como imagen PNG
        print(f"Generando diagrama ER en {output_path}")
        # Comprobar si el DSL parece ser una URL SQLAlchemy (mysql://, sqlite://, etc.)
        is_sqlalchemy_url = False
        if body["dsl"].strip().startswith(("sqlite://", "postgresql://", "mysql://", "oracle://", "mssql://")):
            is_sqlalchemy_url = True
        if is_sqlalchemy_url:
            print("Detectado SQLAlchemy URL, pasando directamente a renderización.")
            # Si es SQLite y el archivo no existe, crearlo con una tabla de ejemplo
            if body["dsl"].strip().startswith("sqlite://"):
                import sqlite3
                import re
                # Extraer ruta del archivo SQLite
                match = re.match(r"sqlite:///(.*)", body["dsl"].strip())
                if match:
                    db_path = match.group(1)
                    if not os.path.exists(db_path):
                        print(f"No existe {db_path}, creando base de datos de ejemplo...")
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name VARCHAR)''')
                        conn.commit()
                        conn.close()
            try:
                render_er(body["dsl"], output_path)  # Pasar URL directamente
            except Exception as e:
                print(f"Error durante el renderizado: {str(e)}")
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': f"Error durante el renderizado: {str(e)}"}),
                    'headers': {'Content-Type': 'application/json'}
                }
        else:
            # Si no es una URL SQLAlchemy, usar el archivo .dsl
            try:
                render_er(dsl_path, output_path)
            except Exception as e:
                print(f"Error durante el renderizado: {str(e)}")
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': f"Error durante el renderizado: {str(e)}"}),
                    'headers': {'Content-Type': 'application/json'}
                }

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

def generar_diagrama_sqlite_local():
    """
    Función utilitaria para pruebas locales: genera un diagrama ER a partir de una base de datos SQLite,
    igual que el test.py.
    """
    import sqlite3
    db_path = 'test.db'
    # Crea una base de datos SQLite de ejemplo con varias tablas y relaciones
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name VARCHAR,
        email VARCHAR
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        title VARCHAR,
        content TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY,
        post_id INTEGER,
        user_id INTEGER,
        comment TEXT,
        FOREIGN KEY(post_id) REFERENCES posts(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()
    # Genera el diagrama
    output_path = 'diagrama_er.png'
    render_er(f'sqlite:///{db_path}', output_path)
    if os.path.exists(output_path):
        print(f"¡Diagrama generado como {output_path}!")
    else:
        print("No se generó el diagrama.")

def generar_diagrama_desde_sqlite_url(sqlite_url, output_path='diagrama_er.png'):
    """
    Genera un diagrama ER a partir de una URL de base de datos SQLite (por ejemplo, 'sqlite:///test.db').
    """
    from eralchemy import render_er
    import os
    render_er(sqlite_url, output_path)
    if os.path.exists(output_path):
        print(f"¡Diagrama generado como {output_path}!")
    else:
        print("No se generó el diagrama.")

if __name__ == "__main__":
    print("Modo interactivo: Ingresa la ruta de tu base de datos SQLite (por ejemplo, test.db):")
    db_path = input("Ruta de la base de datos SQLite: ").strip()
    if not db_path:
        print("No se ingresó una ruta de base de datos.")
    else:
        sqlite_url = f"sqlite:///{db_path}"
        generar_diagrama_desde_sqlite_url(sqlite_url)
