import subprocess

def lambda_handler(event, context):
    try:
        # Ejecutar el comando 'dot' para verificar si Graphviz funciona
        result = subprocess.run(['dot', '-V'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        
        return {
            'statusCode': 200,
            'body': f"Graphviz version: {output}"
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error ejecutando Graphviz: {str(e)}"
        }
