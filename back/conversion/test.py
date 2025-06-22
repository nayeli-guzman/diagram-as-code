from diagrams import Cluster, Diagram 
from diagrams.aws.compute import ECS, EKS, Lambda
from diagrams.aws.database import Redshift
from diagrams.aws. integration import SQS
from diagrams.aws.storage import S3
from diagrams.onprem.vcs import Github
from diagrams.onprem.client import Users
from tempfile import NamedTemporaryFile
import shutil
import json
user_validar = f"diagram-usuarios-dev-validar"
bucket_name = "cad-diagrams"

def lambda_handler(event, context):
    
    code = "from diagrams import Cluster, Diagram\nfrom diagrams.aws.compute import ECS, EKS, Lambda\nfrom diagrams.aws.database import Redshift\nfrom diagrams.aws.storage import S3\nfrom diagrams.onprem.vcs import Github\nfrom diagrams.onprem.client import Users\n\nwith Diagram(\"Event Processing\", show=False):\n    source = EKS(\"k8s source\")\n    with Cluster (\"Event Flows\"):\n        with Cluster (\"Event Workers\"):\n            workers = [ECS(\"worker1\"),\n                        ECS (\"worker2\"),\n                        ECS (\"worker3\" )]\n            queue = SQS(\"event queue\")\n            with Cluster (\"Processing\"):\n                handlers = [Lambda(\"proc1\"),\n                            Lambda (\"proc2\"),\n                            Lambda (\"proc3\" )]\n    store = S3(\"events store\")\n    dw = Redshift (\"analytics\")\n    source >> workers >> queue >> handlers\n    handlers >> store\n    handlers >> dw"

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
        }

        print(safe_locals)
        
        exec(code, {}, safe_locals)

        print("SUCCESS")

    
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f"Error al ejecutar el código: {str(e)}"}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    
lambda_handler({}, {})
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