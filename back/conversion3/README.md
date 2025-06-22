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

## Notas

- El servicio usa un layer de Graphviz preconfigurado en AWS
- El timeout está configurado a 60 segundos
- Las imágenes se devuelven en formato base64
- CORS está habilitado para requests desde el browser
