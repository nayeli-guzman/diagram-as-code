# todo va a estar bien 😀

## Entregables

Editado y Pulido
http://frontend-bucket-s3-v2.s3-website-us-east-1.amazonaws.com

Anterior
http://frontend-hackaton-cloud.s3-website-us-east-1.amazonaws.com/


Ruta ingreso: 
{
  "user_id":   "pedro@utec.edu.pe",
  "tenant_id": "utec",
  "password":  "Secreto123!"
}

probar txt de GH
- https://github.com/nayeli-guzman/diagram-as-code/blob/main/test/aws.txt
- https://github.com/nayeli-guzman/diagram-as-code/blob/main/test/e-r.txt

## 🎯 Objetivo
Diseñar y desarrollar una aplicación web completamente serverless, basada en la infraestructura de AWS, que proporcione un entorno visual e interactivo para la definición y renderización de diagramas técnicos a partir de código fuente.

## ☁️ Arquitectura AWS
- **Frontend**: React (Next.js) desplegado en S3/CloudFront.  
- **API Gateway**: Exposición de endpoints REST protegidos por JWT.  
- **Lambda Functions**: Generación de diagramas (Diagrams, ERAlchemy) y procesamiento de código.  
- **S3**: Almacenamiento de diagramas (PNG, SVG, PDF) y código fuente original, organizados por tipo de diagrama.  

## 🗄️ Tipos de Diagramas
1. **AWS**: Diagramas de arquitectura en la nube.  
2. **E-R**: Diagramas entidad-relación.  
3. **JSON**: Estructuras JSON.  

## ⚙️ Requerimientos Funcionales

### Frontend
- Página de signup/login para autenticación.  
- Editor embebido para escribir código.  
- Opción para subir archivo con definición del diagrama (`.txt` / `.py`).  
- Funcionalidad para pegar texto desde el portapapeles.  
- Botón **Generar diagrama** que envía el código al backend.  
- Visualización del diagrama sólo tras generar.  
- Visualización como imagen (SVG, PNG, PDF).  
- Exportación en PNG, SVG y PDF.  
- Selector de tipo de diagrama (AWS, E-R, JSON).  
- Validación de que haya código antes de enviar.  
- Carga de código desde URL de GitHub.

### Backend (API REST)
- Endpoints protegidos por token.  
- Validación de formato y contenido del código.  
- Generación de diagramas con:
  - [Diagrams](https://diagrams.mingrammer.com/) (AWS, Network).  
  - [ERAlchemy](https://eralchemy.readthedocs.io/) (E-R).  
  - Renderizado y conversión a PNG/SVG/PDF.  
- Almacenamiento en S3 con estructura:
