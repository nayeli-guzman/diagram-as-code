from diagrams import Cluster, Diagram 
from diagrams.aws.compute import ECS, EKS, Lambda
from diagrams.aws.database import Redshift
from diagrams.aws. integration import SQS
from diagrams.aws.storage import S3
from diagrams.onprem.vcs import Github
from diagrams.onprem.client import Users
from tempfile import NamedTemporaryFile

code = "from diagrams import Cluster, Diagram\nfrom diagrams.aws.compute import ECS, EKS, Lambda\nfrom diagrams.aws.database import Redshift\nfrom diagrams.aws.storage import S3\nfrom diagrams.onprem.vcs import Github\nfrom diagrams.onprem.client import Users\n\nwith Diagram(\"Event Processing\", show=False):\n    source = EKS(\"k8s source\")\n    with Cluster (\"Event Flows\"):\n        with Cluster (\"Event Workers\"):\n            workers = [ECS(\"worker1\"),\n                        ECS (\"worker2\"),\n                        ECS (\"worker3\" )]\n            queue = SQS(\"event queue\")\n            with Cluster (\"Processing\"):\n                handlers = [Lambda(\"proc1\"),\n                            Lambda (\"proc2\"),\n                            Lambda (\"proc3\" )]\n    store = S3(\"events store\")\n    dw = Redshift (\"analytics\")\n    source >> workers >> queue >> handlers\n    handlers >> store\n    handlers >> dw"
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
exec(code, {}, safe_locals)
