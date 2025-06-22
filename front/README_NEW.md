# Diagram as Code - Frontend

> ❤️ **Desarrollado por el grupo "Todo va a estar Bien"** para el UTEC Hackathon 2025

Aplicación web React + TypeScript + Tailwind para generar diagramas de arquitectura usando **Diagrams.py**.

## 🚀 Características

### ✅ Autenticación de Usuario

- **Login/Signup** con email y contraseña
- Token JWT almacenado en localStorage
- Rutas protegidas con autenticación
- Sesión persistente

### ✅ Editor Embebido

- **Monaco Editor** (mismo de VS Code) con syntax highlighting para Python
- Tema oscuro configurado
- Auto-completado y validación básica
- Carga de archivos `.py` o `.txt`

### ✅ Selector de Tipo de Diagrama

- Soporte para múltiples providers de Diagrams.py:
  - **AWS** - Amazon Web Services
  - **Azure** - Microsoft Azure
  - **GCP** - Google Cloud Platform
  - **Kubernetes** - K8s Resources
  - **Network** - Network Architecture
  - **On-Premise** - On-Premise Infrastructure
  - **Programming** - Programming Languages
  - **Generic** - Generic Components

### ✅ Generación de Diagramas

- Validación local del código Python
- Llamadas API al backend con autenticación JWT
- Manejo de errores con toast notifications
- Spinner de carga durante generación

### ✅ Visualización Interactiva

- Preview del diagrama generado (SVG/PNG)
- **Zoom** in/out con controles (+/-)
- **Reset zoom** para vista original
- Scroll para diagramas grandes
- Responsive design

### ✅ Exportación

- **Descarga directa** desde URL del backend
- Soporte para SVG y PNG
- Botón de descarga con icono

### ✅ Validaciones y Feedback

- Validación de código no vacío
- Verificación de imports de diagrams
- Toast notifications para errores/éxito
- Mensajes de error claros del backend

### ✅ Carga desde GitHub

- Input para URL de archivo en GitHub
- Conversión automática a raw URL
- Carga del contenido en el editor
- Manejo de errores de red

## 🛠️ Tecnologías Utilizadas

- **React 19** - Framework principal
- **TypeScript** - Tipado estático
- **Tailwind CSS** - Styling y diseño
- **Vite** - Build tool y dev server
- **Monaco Editor** - Editor de código
- **React Router** - Navegación
- **React Hot Toast** - Notificaciones
- **Lucide React** - Iconos

## 📦 Instalación

```bash
# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env
# Editar .env con la URL del backend

# Ejecutar en desarrollo
npm run dev

# Build para producción
npm run build
```

## 🔧 Configuración

### Variables de Entorno

```env
VITE_API_URL=http://localhost:8000/api
```

### Estructura del Proyecto

```
src/
├── components/           # Componentes React
│   ├── Login.tsx        # Página de login
│   ├── Signup.tsx       # Página de registro
│   ├── DiagramEditor.tsx # Editor principal
│   └── ProtectedRoute.tsx # HOC para rutas protegidas
├── contexts/            # Context providers
│   └── AuthContext.tsx  # Contexto de autenticación
├── hooks/              # Custom hooks
│   └── useAuth.ts      # Hook de autenticación
├── types/              # Definiciones de tipos
│   └── index.ts        # Interfaces TypeScript
├── utils/              # Utilidades
│   └── api.ts          # Cliente API y helpers
├── App.tsx             # Componente raíz con router
└── main.tsx           # Entry point
```

## 🔑 API Backend

La aplicación espera un backend con los siguientes endpoints:

### Autenticación

```
POST /api/auth/login
POST /api/auth/signup
GET  /api/auth/verify
```

### Generación de Diagramas

```
POST /api/diagrams/generate
```

Ejemplo de payload:

```json
{
  "code": "from diagrams import Diagram...",
  "type": "aws"
}
```

Respuesta esperada:

```json
{
  "imageUrl": "https://your-backend.com/generated/diagram.svg",
  "success": true
}
```

## 🚀 Scripts Disponibles

```bash
npm run dev      # Servidor de desarrollo
npm run build    # Build para producción
npm run preview  # Preview del build
npm run lint     # Linter ESLint
```

## 📝 Uso

1. **Registro/Login**: Crea una cuenta o inicia sesión
2. **Seleccionar tipo**: Elige el tipo de diagrama (AWS, Azure, etc.)
3. **Escribir código**: Usa el editor Monaco para escribir Python con Diagrams.py
4. **Generar**: Haz clic en "Generar Diagrama"
5. **Visualizar**: Ve el resultado en el panel derecho
6. **Exportar**: Descarga el diagrama en el formato deseado

## 🔧 Personalización

### Nuevos Tipos de Diagrama

Para agregar un nuevo tipo de diagrama:

1. Actualiza el tipo `DiagramType` en `src/types/index.ts`
2. Añade la nueva opción en `diagramTypes` en `DiagramEditor.tsx`
3. Crea un placeholder en `getPlaceholderCode()`

### Temas del Editor

El editor Monaco usa tema oscuro por defecto. Para cambiarlo:

```tsx
<Editor
  theme="vs-light" // o "vs-dark", "hc-black"
  // ...otros props
/>
```

## 📄 Licencia

MIT License
