import boto3, json, os
from eralchemy import render_er
import tempfile

bucket_name = "mi-bucket-diagrams"
output_path = "/tmp/diagrama_er.png"
user_validar = f"diagram-usuarios-dev-validar"

cors_headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'POST, OPTIONS'
}

def lambda_handler(event, context):
    print(event)
    body = json.loads(event['body'])
    # Solo permitir 'code' como campo válido
    code = body.get('code')

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
            'headers': cors_headers
        }
    # Si el token es válido, continuar con la creación del diagrama
    if not code or not user_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Falta code o user_id'}),
            'headers': cors_headers
        }
    try:
        # Verificar si /tmp existe y es escribible
        if not os.path.exists('/tmp'):
            os.makedirs('/tmp')  # Crear directorio si no existe
        if not os.access('/tmp', os.W_OK):
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'El directorio /tmp no es escribible'}),
                'headers': cors_headers
            }
        # Preprocesar el código: Limpiar caracteres de escape y saltos de línea
        code_cleaned = code.replace("\\n", "\n").replace("\\t", "\t").strip()
        print(f"Código limpio:\n{code_cleaned}")  # Verifica si el código se limpió correctamente
        # Detectar si el código es SQL (CREATE TABLE, etc.)
        sql_keywords = ["CREATE TABLE", "create table", "CREATE INDEX", "create index", "ALTER TABLE", "alter table"]
        if any(code_cleaned.strip().startswith(kw) for kw in sql_keywords):
            ok = crear_sqlite_y_diagrama_desde_sql(code_cleaned, output_path, user_id)
            if not ok:
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': f"No se pudo generar el diagrama ER a partir del SQL proporcionado."}),
                    'headers': cors_headers
                }
            # Subir a S3
            s3 = boto3.client("s3")
            import uuid
            safe_user_id = user_id.replace('@', '_').replace('.', '_')
            s3_key = f"er-diagrama-{safe_user_id}-{uuid.uuid4()}.png"
            print(f"Subiendo el archivo {output_path} a S3 con la clave {s3_key}")
            s3.upload_file(
                output_path,
                bucket_name,
                s3_key,
                ExtraArgs={'ContentType': 'image/png', 'ACL': 'public-read'}
            )
            image_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({'imageUrl': image_url})
            }
        # Si es una URL SQLAlchemy (sqlite://, mysql://, etc.)
        is_sqlalchemy_url = False
        if code_cleaned.strip().startswith(("sqlite://", "postgresql://", "mysql://", "oracle://", "mssql://")):
            is_sqlalchemy_url = True
        if is_sqlalchemy_url:
            print("Detectado SQLAlchemy URL, pasando directamente a renderización.")
            # Si es SQLite y el archivo no existe, crearlo con una tabla de ejemplo
            if code_cleaned.strip().startswith("sqlite://"):
                import sqlite3
                import re
                match = re.match(r"sqlite:///(.*)", code_cleaned.strip())
                if match:
                    db_path = match.group(1)
                    if not db_path.startswith("/"):
                        db_path = f"/tmp/{db_path}"
                    if not os.path.exists(db_path):
                        print(f"No existe {db_path}, creando base de datos de ejemplo...")
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name VARCHAR)''')
                        conn.commit()
                        conn.close()
                    code_cleaned = f"sqlite:///{db_path}"
            try:
                render_er(code_cleaned, output_path)
            except Exception as e:
                print(f"Error durante el renderizado: {str(e)}")
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': f"Error durante el renderizado: {str(e)}"}),
                    'headers': cors_headers
                }
        else:
            # Si no es SQL ni URL, asumir archivo DBML/DSL
            try:
                # Escribir código limpio a archivo temporal
                with tempfile.NamedTemporaryFile(delete=False, suffix=".dsl", mode='w') as dsl_file:
                    dsl_file.write(code_cleaned)
                    dsl_path = dsl_file.name
                    print(f"DSL Path creado: {dsl_path}")
                render_er(dsl_path, output_path)
            except Exception as e:
                print(f"Error durante el renderizado: {str(e)}")
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': f"Error durante el renderizado: {str(e)}"}),
                    'headers': cors_headers
                }
        # Verificar si la imagen se generó correctamente
        if not os.path.exists(output_path):
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f"El archivo de imagen no se generó correctamente: {output_path}"}),
                'headers': cors_headers
            }
        # Subir a S3
        s3 = boto3.client("s3")
        s3_key = f"er-diagrama-{user_id}.png"
        print(f"Subiendo el archivo {output_path} a S3 con la clave {s3_key}")
        s3.upload_file(
            output_path,
            bucket_name,
            s3_key,
            ExtraArgs={'ContentType': 'image/png', 'ACL': 'public-read'}
        )
        image_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'imageUrl': image_url})
        }
    except Exception as e:
        # Detallar el error
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Ocurrió un error: {str(e)}'}),
            'headers': cors_headers
        }

def crear_sqlite_y_diagrama_desde_sql(dsl_cleaned, output_path, user_id):
    """
    Crea una base de datos SQLite temporal, ejecuta el SQL recibido y genera el diagrama ER.
    Devuelve True si el diagrama se generó correctamente, False en caso contrario.
    """
    import sqlite3, uuid, time
    db_path = f"/tmp/{user_id.replace('@','_').replace('.','_')}_{uuid.uuid4().hex}.db"
    print(f"Creando base de datos temporal en {db_path} y ejecutando SQL del usuario...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON;')
        cursor.executescript(dsl_cleaned)
        # DEBUG: Listar tablas y relaciones
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tablas creadas: {tables}")
        for table in tables:
            cursor.execute(f"PRAGMA foreign_key_list({table[0]});")
            fks = cursor.fetchall()
            print(f"Foreign keys en {table[0]}: {fks}")
        conn.commit()
        conn.close()
        time.sleep(0.1)  # Espera breve para asegurar que el archivo esté listo
        # Generar el diagrama
        render_er(f"sqlite:///{db_path}", output_path)
        if os.path.exists(output_path):
            print(f"¡Diagrama generado como {output_path}!")
            return True
        else:
            print("No se generó el diagrama.")
            return False
    except Exception as e:
        print(f"Error ejecutando SQL: {str(e)}")
        return False

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
