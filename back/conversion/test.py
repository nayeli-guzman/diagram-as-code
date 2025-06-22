from diagrams import Cluster, Diagram 
from diagrams.aws.compute import ECS, EKS, Lambda
from diagrams.aws.database import Redshift
from diagrams.aws. integration import SQS
from diagrams.aws.storage import S3
from diagrams.onprem.vcs import Github
from diagrams.onprem.client import Users
from diagrams.aws.network import Route53

with Diagram("Event Processing", show=False, outformat='png', filename='./tmp/diagrama.png'):
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