import re

code ="with Diagram(\"Event Processing\", show=False):\n    source = EKS(\"k8s source\")\n    with Cluster(\"Event Flows\"):\n        with Cluster(\"Event Workers\"):\n            workers = [ECS(\"worker1\"),\n                       ECS(\"worker2\"),\n                       ECS(\"worker3\")]\n            queue = SQS(\"event queue\")\n            with Cluster(\"Processing\"):\n                handlers = [Lambda(\"proc1\"),\n                            Lambda(\"proc2\"),\n                            Lambda(\"proc3\")]\n    store = S3(\"events store\")\n    dw = Redshift(\"analytics\")\n    source >> workers >> queue >> handlers\n    handlers >> store\n    handlers >> dw\n"

modified_code = re.sub(r"^with Diagram\([^\)]*\):\n", 
                      r"with Diagram(\"gen\", show=False, outformat='png', filename='/tmp/diagrama'):\n", 
                      code, flags=re.MULTILINE)

print(modified_code)