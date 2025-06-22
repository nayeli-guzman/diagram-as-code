import os

def lambda_handler(event, context):
    # Verificar si `dot` está en el PATH
    dot_path = '/opt/bin/dot'
    if os.path.exists(dot_path):
        print(f"Graphviz dot found at {dot_path}")
        os.system(f"{dot_path} -V")  # Ejecuta el comando dot para verificar su versión
    else:
        print("Graphviz dot not found!")
    
    return {
        'statusCode': 200,
        'body': "Check the logs for Graphviz status."
    }
