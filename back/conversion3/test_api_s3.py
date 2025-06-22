#!/usr/bin/env python3
"""
Script para probar la API desplegada con funcionalidad S3
"""

import requests
import json
import base64
from datetime import datetime

def test_api_with_s3():
    """Prueba la API desplegada con guardado en S3"""
    
    # URL de tu API desplegada
    api_url = "https://eaeu5ax03c.execute-api.us-east-1.amazonaws.com/dev/generate-diagram"
    
    # Datos de prueba
    payload = {
        "title": "Test Architecture Diagram",
        "bucket": "mi-bucket-diagramas",  # Cambia por tu bucket
        "data": {
            "CloudSystem": {
                "Frontend": {
                    "WebApp": {"react": {}, "routing": {}},
                    "MobileApp": {"ios": {}, "android": {}}
                },
                "Backend": {
                    "API": {"lambda": {}, "gateway": {}},
                    "Database": {"dynamodb": {}, "s3": {}}
                },
                "Infrastructure": {
                    "AWS": {"ec2": {}, "cloudfront": {}},
                    "Monitoring": {"cloudwatch": {}, "xray": {}}
                }
            }
        }
    }
    
    print("🚀 Enviando request a la API...")
    print(f"URL: {api_url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Enviar request
        response = requests.post(
            api_url,
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=30
        )
        
        print(f"\n📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Respuesta exitosa!")
            print(f"Message: {result.get('message')}")
            
            # Guardar imagen localmente desde base64
            if 'image' in result:
                image_data = base64.b64decode(result['image'])
                filename = f"api_test_diagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                with open(filename, 'wb') as f:
                    f.write(image_data)
                print(f"📊 Imagen guardada localmente: {filename}")
            
            # Mostrar información de S3
            if 's3' in result and result['s3']:
                s3_info = result['s3']
                if s3_info.get('success'):
                    print(f"\n☁️ ¡Imagen guardada en S3!")
                    print(f"🌐 URL pública: {s3_info.get('url')}")
                    print(f"📁 Bucket: {s3_info.get('bucket')}")
                    print(f"🔑 Key: {s3_info.get('key')}")
                else:
                    print(f"\n❌ Error en S3: {s3_info.get('error')}")
                    print("💡 Asegúrate de que el bucket existe y tienes permisos")
            else:
                print("\n📝 No se especificó bucket S3, solo se generó base64")
        
        else:
            print(f"❌ Error en la API: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - La request tardó más de 30 segundos")
    except requests.exceptions.RequestException as e:
        print(f"🔌 Error de conexión: {e}")
    except Exception as e:
        print(f"💥 Error inesperado: {e}")

def test_api_without_s3():
    """Prueba la API sin S3 (comportamiento original)"""
    
    api_url = "https://eaeu5ax03c.execute-api.us-east-1.amazonaws.com/dev/generate-diagram"
    
    payload = {
        "title": "Simple Test",
        "data": {
            "App": {
                "Frontend": {"ui": {}},
                "Backend": {"api": {}}
            }
        }
    }
    
    print("\n🧪 Probando sin S3...")
    
    try:
        response = requests.post(api_url, headers={'Content-Type': 'application/json'}, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API funcionando correctamente sin S3")
            print(f"Message: {result.get('message')}")
            print(f"Tiene imagen base64: {'image' in result}")
            print(f"Info S3: {result.get('s3', 'No hay info S3')}")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    print("🔧 Probando API de Diagramas con S3")
    print("=" * 50)
    
    # Probar con S3
    test_api_with_s3()
    
    # Probar sin S3
    test_api_without_s3()
    
    print("\n✨ Pruebas completadas!")
