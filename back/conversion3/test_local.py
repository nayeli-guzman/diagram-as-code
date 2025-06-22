#!/usr/bin/env python3
"""
Script para probar el handler de Lambda localmente
"""

import json
import base64
from lambda_handler import lambda_handler

def test_local():
    """Prueba el handler localmente"""
    
    # Simular un evento de API Gateway
    event = {
        'body': json.dumps({
            'title': 'Mi Tienda Online',
            'bucket': 'mi-bucket-diagramas',  # Nuevo: especificar bucket S3
            'data': {
                "Mi_Empresa": {
                    "Ventas": {
                        "Online": {"web": {}, "app": {}},
                        "Fisica": {"tienda1": {}, "tienda2": {}}
                    },
                    "Inventario": {
                        "Productos": {"categoria_a": {}, "categoria_b": {}},
                        "Almacenes": {"principal": {}, "secundario": {}}
                    }
                }
            }
        })
    }
    
    context = {}
    
    # Ejecutar el handler
    response = lambda_handler(event, context)
    
    print(f"Status Code: {response['statusCode']}")
    
    if response['statusCode'] == 200:
        body = json.loads(response['body'])
        print("✅ Diagrama generado exitosamente")
        
        # Guardar la imagen localmente para verificar
        image_data = base64.b64decode(body['image'])
        with open('test_diagram.png', 'wb') as f:
            f.write(image_data)
        print("📊 Imagen guardada como: test_diagram.png")
        
        # Mostrar información de S3 si está disponible
        if 's3' in body and body['s3']:
            s3_info = body['s3']
            if s3_info.get('success'):
                print(f"☁️ Imagen subida a S3: {s3_info.get('url')}")
                print(f"📁 Bucket: {s3_info.get('bucket')}")
                print(f"🔑 Key: {s3_info.get('key')}")
            else:
                print(f"❌ Error en S3: {s3_info.get('error')}")
    else:
        print(f"❌ Error: {response['body']}")

if __name__ == '__main__':
    test_local()
