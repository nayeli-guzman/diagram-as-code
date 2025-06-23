FROM public.ecr.aws/lambda/python:3.13

RUN microdnf install -y graphviz zip && \
    microdnf clean all

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY entidad_relacion.py ./

CMD [ "entidad_relacion.lambda_handler" ]
