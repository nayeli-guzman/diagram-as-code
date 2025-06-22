from diagrams import Cluster, Diagram 
from diagrams.aws.compute import ECS, EKS, Lambda
from diagrams.aws.database import Redshift
from diagrams.aws. integration import SQS
from diagrams.aws.storage import S3
from diagrams.onprem.vcs import Github
from diagrams.onprem.client import Users
from diagrams.aws.network import Route53

from tempfile import NamedTemporaryFile
import shutil
import json
import boto3

user_validar = f"diagram-usuarios-dev-validar"
bucket_name = "cad-diagrams"

def lambda_handler(event, context):
    
    print(event)
    # Entrada (json)
    body =  json.loads(event['body'])
    
    # Inicio - Proteger el Lambda
    token = event['headers']['Authorization']
    tenant_id = body['tenant_id']
    user_id = body['user_id']
 
    lambda_client = boto3.client('lambda')    
    payload = {
    "token": token,
    "tenant_id": tenant_id
    }
    invoke_response = lambda_client.invoke(FunctionName=user_validar,
                                           InvocationType='RequestResponse',
                                           Payload = json.dumps(payload))
    response = json.loads(invoke_response['Payload'].read())
    print(response)
    if response['statusCode'] == 403:
        return {
            'statusCode' : 403,
            'status' : 'Forbidden - Acceso No Autorizado'
        }

    code = body["code"]
    code = "import graphviz\n\n# Prueba si Graphviz se puede ejecutar\ntry:\n    print(\"Probando Graphviz\")\n    dot = graphviz.Digraph(comment='Test')\n    dot.node('A', 'Inicio')\n    dot.node('B', 'Fin')\n    dot.edge('A', 'B', 'A -> B')\n    print(\"Diagrama generado correctamente con Graphviz\")\n    dot.render('/tmp/test_diagram', format='png')  # Intenta renderizar el diagrama\nexcept Exception as e:\n    print(f\"Error al usar Graphviz: {str(e)}\")"
    
    '''
    with Diagram("Event Processing", show=False):
        source = EKS("k8s source")
        with Cluster ("Event Flows"):
            with Cluster ("Event Workers"):
                workers = [ECS("worker1"),
                            ECS ("worker2"),
                            ECS ("worker3") ]
                queue = SQS("event queue")
                with Cluster ("Processing"):
                    handlers = [Lambda("proc1"),
                                Lambda ("proc2"),
                                Lambda ("proc3" )]
        store = S3("events store")
        dw = Redshift ("analytics")
        source >> workers >> queue >> handlers
        handlers >> store
        handlers >> dw
    '''
    print(code)

    try:
        safe_locals = {
            'Diagram': Diagram,
            'ECS': ECS,
            'EKS': EKS,
            'Lambda': Lambda,
            'SQS': SQS,
            'S3': S3,
            'Redshift': Redshift,
            'Github': Github,
            'Users': Users,
            'Cluster': Cluster,
            'Route53': Route53,
        }

        print(safe_locals)
        
        exec(code, {}, safe_locals)

        print("SUCCESS")

        with NamedTemporaryFile(delete=False, suffix=".png", dir='/tmp') as tmpfile:
            print("GG")
            tmpfile_path = tmpfile.name 
            print(tmpfile)
            print(tmpfile.name)
            print(f"Saving diagram to {tmpfile_path}")
            s3_client = boto3.client('s3')
            s3_key = f'diagrama-{user_id}.png'
            bucket_name = 'cad-diagrams'
            s3_client.upload_file(tmpfile_path, bucket_name, s3_key)
            print(s3_key)
            
            image_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
            print(f"Image URL: {image_url}")

        return {
            'statusCode': 200,
            'body': json.dumps({'imageUrl': image_url}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f"Error al ejecutar el código: {str(e)}"}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
'''
with Diagram("Event Processing", show=False):
    source = EKS("k8s source")
    with Cluster ("Event Flows"):
        with Cluster ("Event Workers"):
            workers = [ECS("worker1"),
                        ECS ("worker2"),
                        ECS ("worker3") ]
            queue = SQS("event queue")
            with Cluster ("Processing"):
                handlers = [Lambda("proc1"),
                            Lambda ("proc2"),
                            Lambda ("proc3" )]
    store = S3("events store")
    dw = Redshift ("analytics")
    source >> workers >> queue >> handlers
    handlers >> store
    handlers >> dw
'''