FROM public.ecr.aws/lambda/python:3.13

RUN microdnf install -y graphviz zip && \
    microdnf clean all

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY lambda_handler.py jsondi.py ./

CMD [ "lambda_handler.lambda_handler" ]
