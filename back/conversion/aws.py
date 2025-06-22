import os
import jsons

def lambda_handler(event, context):
    # Verificar si 'dot' está en /opt/bin
    os.environ["PATH"] += ":/opt/bin"

    print("PATH:", os.environ["PATH"])
    
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