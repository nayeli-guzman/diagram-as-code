import subprocess

def lambda_handler(event, context):
    # Ejecutar el comando ldd --version para obtener la versión de glibc
    result = subprocess.run(['ldd', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Capturar y mostrar la salida
    stdout = result.stdout.decode()
    stderr = result.stderr.decode()

    print("STDOUT:", stdout)
    print("STDERR:", stderr)

    return {
        'statusCode': 200,
        'body': f"Output: {stdout}, Error: {stderr}"
    }
