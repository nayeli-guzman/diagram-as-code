# Usa la imagen oficial de AWS Lambda para Python 3.13
FROM public.ecr.aws/lambda/python:3.13

# Instala Graphviz (binarios + librerías) usando microdnf
RUN microdnf install -y graphviz zip && \
    microdnf clean all

# Copia e instala tus dependencias de Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia tu código de la función
COPY lambda_handler.py jsondi.py ./

# Define el handler de Lambda
CMD [ "lambda_handler.lambda_handler" ]
