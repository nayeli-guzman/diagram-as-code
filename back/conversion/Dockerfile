FROM public.ecr.aws/lambda/python:3.13

RUN microdnf install -y graphviz zip && \
    microdnf clean all

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY aws.py ./

CMD [ "aws.lambda_handler" ]
