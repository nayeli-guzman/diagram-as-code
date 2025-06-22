import os
import json

def lambda_handler(event, context):
    # Verificar si 'dot' está en /opt/bin
    print(os.environ["PATH"])
    os.environ["PATH"] += ":/opt/bin"
    print(os.environ["PATH"])
    path_env = os.environ.get("PATH")
    
    bin_dir = ':/opt/bin'
    try:
        path_directories = path_env.split(':')

        # Imprimir cada directorio
        for directory in path_directories:
            print(f"Directorio: {directory}")
        print("sssss")
        
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Contenido de /opt/bin impreso correctamente.'}),
            'headers': {'Content-Type': 'application/json'}
        }
        
    except FileNotFoundError:
        print("gggg")
        pass

    # Ejecutar el comando dot para verificar su versión
    result = os.system("dot -V")
    
    if result != 0:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Graphviz no está disponible o no se encuentra en el PATH.'}),
            'headers': {'Content-Type': 'application/json'}
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Graphviz está disponible y el diagrama fue generado correctamente.'}),
        'headers': {'Content-Type': 'application/json'}
    }
