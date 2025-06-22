import json
import base64
import io
import tempfile
import os
import boto3
from datetime import datetime
import uuid
from graphviz import Digraph

def json_to_graph(data, graph=None, parent=None, level=0):
    """Convierte estructura JSON a grafo de Graphviz"""
    
    if graph is None:
        graph = Digraph(comment='Estructura JSON')
        graph.attr(rankdir='TB')
        graph.attr('node', shape='rectangle', style='rounded,filled')
        graph.attr('edge', color='#666666')
    
    # Colores por nivel
    colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightcoral', 'lightpink', 'lightgray']
    color = colors[min(level, len(colors)-1)]
    
    for key, value in data.items():
        node_id = f"{parent}_{key}" if parent else key
        
        # Crear nodo con formato dependiendo del nivel
        if level == 0:
            # Nodo raíz
            graph.node(node_id, f"🏢 {key}", fillcolor=color, fontsize='16', fontweight='bold')
        elif level == 1:
            # Nodos principales
            graph.node(node_id, f"📁 {key}", fillcolor=color, fontsize='14', fontweight='bold')
        elif level == 2:
            # Nodos secundarios
            graph.node(node_id, f"📂 {key}", fillcolor=color, fontsize='12')
        else:
            # Nodos de detalle
            graph.node(node_id, f"📄 {key}", fillcolor=color, fontsize='10')
        
        # Crear conexión con el padre
        if parent:
            graph.edge(parent, node_id)
        
        # Procesar hijos recursivamente
        if isinstance(value, dict) and value:
            json_to_graph(value, graph, node_id, level + 1)
        elif isinstance(value, dict) and not value:
            # Nodo vacío (hoja)
            empty_id = f"{node_id}_empty"
            graph.node(empty_id, "📋 (vacío)", shape='ellipse', fillcolor='white', fontsize='8')
            graph.edge(node_id, empty_id, style='dashed', color='lightgray')
    
    return graph

def generar_diagrama_json_lambda(data, title="Diagrama JSON"):
    """Genera un diagrama JSON y devuelve los bytes de la imagen"""
    
    try:
        # Crear el grafo
        graph = json_to_graph(data)
        graph.attr(label=title, fontsize='18', fontweight='bold')
        
        # Usar un directorio temporal
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = os.path.join(temp_dir, "diagram")
            
            # Renderizar como PNG
            graph.render(filename, format='png', cleanup=True)
            
            # Leer el archivo PNG generado
            with open(f"{filename}.png", 'rb') as f:
                image_bytes = f.read()
            
            return image_bytes
    
    except Exception as e:
        raise Exception(f"Error generando diagrama: {str(e)}")

def generar_estructura_ecommerce():
    """Genera un diagrama de estructura JSON simple para un sistema de ecommerce"""
    
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

def upload_to_s3(image_bytes, bucket_name, title="diagram"):
    """Sube la imagen a S3 y retorna la URL y key"""
    
    try:
        # Crear cliente S3
        s3_client = boto3.client('s3')
        
        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"diagrams/{title.replace(' ', '_')}_{timestamp}_{unique_id}.png"
        
        # Subir archivo a S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=image_bytes,
            ContentType='image/png',
            ACL='public-read'  # Hace el archivo público
        )
        
        # Generar URL pública
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{filename}"
        
        return {
            'success': True,
            'url': s3_url,
            'key': filename,
            'bucket': bucket_name
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Error subiendo a S3: {str(e)}"
        }

def lambda_handler(event, context):
    """Handler principal de AWS Lambda"""
    
    try:
        # Parsear el body del request
        if 'body' in event:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            body = {}
        
        # Obtener datos JSON del request o usar ejemplo por defecto
        if 'data' in body:
            json_data = body['data']
        else:
            # Si no se envían datos, usar estructura de ecommerce por defecto
            json_data = generar_estructura_ecommerce()
        
        # Obtener título opcional
        title = body.get('title', 'Estructura JSON')
        
        # Generar el diagrama
        image_bytes = generar_diagrama_json_lambda(json_data, title)
        
        # Convertir a base64 para devolverlo en la respuesta HTTP
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Subir a S3 si se proporciona el nombre del bucket
        s3_response = {}
        if 'bucket' in body:
            bucket_name = body['bucket']
            s3_response = upload_to_s3(image_bytes, bucket_name, title)
        
        # Respuesta exitosa
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Diagrama generado exitosamente',
                'image': image_base64,
                'contentType': 'image/png',
                's3': s3_response
            })
        }
    
    except Exception as e:
        # Respuesta de error
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }
