import json
import base64
import io
import tempfile
import os
import boto3
from datetime import datetime
import uuid
from graphviz import Digraph

user_validar = f"diagram-usuarios-dev-validar"
bucket_name = "mi-bucket-diagrams"

def json_to_graph(data, graph=None, parent=None, level=0):
    
    if graph is None:
        graph = Digraph(comment='Estructura JSON')
        graph.attr(rankdir='TB')
        graph.attr('node', shape='rectangle', style='rounded,filled')
        graph.attr('edge', color='#666666')
    
    colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightcoral', 'lightpink', 'lightgray']
    color = colors[min(level, len(colors)-1)]
    
    for key, value in data.items():
        node_id = f"{parent}_{key}" if parent else key
        if level == 0:
            graph.node(node_id, f"🏢 {key}", fillcolor=color, fontsize='16', fontweight='bold')
        elif level == 1:
            graph.node(node_id, f"📁 {key}", fillcolor=color, fontsize='14', fontweight='bold')
        elif level == 2:
            graph.node(node_id, f"📂 {key}", fillcolor=color, fontsize='12')
        else:
            graph.node(node_id, f"📄 {key}", fillcolor=color, fontsize='10')
        
        if parent:
            graph.edge(parent, node_id)
        
        if isinstance(value, dict) and value:
            json_to_graph(value, graph, node_id, level + 1)
        elif isinstance(value, dict) and not value:
            empty_id = f"{node_id}_empty"
            graph.node(empty_id, "📋 (vacío)", shape='ellipse', fillcolor='white', fontsize='8')
            graph.edge(node_id, empty_id, style='dashed', color='lightgray')
    
    return graph

def generate_random():
    return {
        "Tienda_Online": {
            "Usuarios": {
                "Clientes": {"perfil": {}, "historial": {}},
                "Admins": {"panel": {}}
            },
            "Productos": {
                "Categorias": {"electronica": {}, "ropa": {}},
                "Stock": {"disponible": {}, "agotado": {}}
            },
            "Pedidos": {
                "Estado": {"pendiente": {}, "enviado": {}},
                "Pago": {"tarjeta": {}, "efectivo": {}}
            }
        }
    }

def upload_to_s3(filepath, user_id, bucket_name):

    try:
        s3_client = boto3.client('s3')        
        hash = str(uuid.uuid4())
        s3_key = f'diagrama-json-{user_id}-{hash}.png'
    
        s3_client.upload_file(
            Filename=filepath, 
            Bucket=bucket_name,                     
            Key=s3_key,                          
            ExtraArgs={'ACL': 'public-read'}             
        )
            
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
        
        return {
            'success': True,
            'url': s3_url,
            'bucket': bucket_name
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Error subiendo a S3: {str(e)}"
        }

def lambda_handler(event, context):
    
    print(event)
    body = json.loads(event.get('body', '{}'))
    
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
    
    # generando el diagrama

    code = json.loads(body['code']) if 'code 'in body else generate_random()
    title = body['title'] if 'title' in body else "Diagrama JSON"
    filepath = "tmp/diagrama"

    print(code)

    try:
        graph = json_to_graph(code)
        graph.attr(label=title, fontsize='18', fontweight='bold')
        graph.render(filepath, format='png', cleanup=True)
            
    except Exception as e:
        raise Exception(f"Error generando diagrama: {str(e)}")

    
    s3_response = {}
    
    s3_response = upload_to_s3(f"{filepath}.png", user_id, bucket_name)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps({
            'message': 'Diagrama generado exitosamente',
            'contentType': 'image/png',
            's3': s3_response
        })
    }
    
