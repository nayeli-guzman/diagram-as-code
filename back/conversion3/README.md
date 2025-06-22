# Generador de Diagramas JSON - AWS Lambda

Este proyecto convierte estructuras JSON en diagramas visuales usando AWS Lambda y Serverless Framework.

## Estructura del Proyecto

```
├── serverless.yml          # Configuración de Serverless Framework
├── lambda_handler.py       # Handler principal de Lambda
├── requirements.txt        # Dependencias de Python
├── test_local.py          # Script para pruebas locales
└── README.md              # Este archivo
```

## Instalación

### 1. Instalar Serverless Framework

```bash
npm install -g serverless
```

### 2. Instalar plugins necesarios

```bash
npm install serverless-python-requirements
```

### 3. Configurar AWS CLI (si no está configurado)

```bash
aws configure
```

## Deployment

### Desplegar a AWS

```bash
serverless deploy
```

### Remover el deployment

```bash
serverless remove
```

## Uso

### 1. Endpoint

```
POST https://tu-api-gateway-url.amazonaws.com/dev/generate-diagram
```

### 2. Formato del Request

```json
{
  "title": "Mi Diagrama",
  "data": {
    "Empresa": {
      "Departamentos": {
        "Ventas": { "equipo_a": {}, "equipo_b": {} },
        "Marketing": { "digital": {}, "tradicional": {} }
      }
    }
  }
}
```

### 3. Formato de la Respuesta

```json
{
  "success": true,
  "message": "Diagrama generado exitosamente",
  "image": "base64-encoded-png-image",
  "contentType": "image/png"
}
```

## Prueba Local

Para probar localmente antes del deployment:

```bash
python test_local.py
```

Este comando generará un archivo `test_diagram.png` para verificar que todo funciona.

## Ejemplo de uso con curl

```bash
curl -X POST https://tu-api-url/generate-diagram \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mi Sistema",
    "data": {
      "Sistema": {
        "Frontend": {"web": {}, "mobile": {}},
        "Backend": {"api": {}, "database": {}}
      }
    }
  }'
```

## 🆕 Nueva Funcionalidad: Guardar en S3

Ahora puedes guardar automáticamente los diagramas en un bucket S3:

### Ejemplo con S3

```bash
curl -X POST https://eaeu5ax03c.execute-api.us-east-1.amazonaws.com/dev/generate-diagram \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mi Arquitectura",
    "bucket": "mi-bucket-diagramas",
    "data": {
      "Sistema": {
        "Frontend": {"web": {}, "mobile": {}},
        "Backend": {"api": {}, "database": {}}
      }
    }
  }'
```

### Respuesta con S3

```json
{
  "success": true,
  "message": "Diagrama generado exitosamente",
  "image": "base64-encoded-image",
  "contentType": "image/png",
  "s3": {
    "success": true,
    "url": "https://mi-bucket-diagramas.s3.amazonaws.com/diagrams/Mi_Arquitectura_20250622_143052_a1b2c3d4.png",
    "key": "diagrams/Mi_Arquitectura_20250622_143052_a1b2c3d4.png",
    "bucket": "mi-bucket-diagramas"
  }
}
```

### Parámetros para S3

- `bucket` (opcional): Nombre del bucket S3 donde guardar la imagen
- Si no se especifica `bucket`, solo se devuelve el base64 sin guardar en S3
