import React, { useState, useRef, useCallback } from "react";
import Editor from "@monaco-editor/react";
import {
  Play,
  Upload,
  Github,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  LogOut,
  FileText,
  ImageIcon,
  FileImage,
  FileText as FilePdf,
} from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { githubAPI } from "../utils/api";
import toast from "react-hot-toast";
import type { DiagramType } from "../types";
import { saveAs } from "file-saver";
import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";

const DiagramEditor: React.FC = () => {
  const [code, setCode] = useState("");
  const [diagramType, setDiagramType] = useState<DiagramType>("aws");
  const [generatedImageUrl, setGeneratedImageUrl] = useState<string | null>(
    null
  );
  const [isGenerating, setIsGenerating] = useState(false);
  const [githubUrl, setGithubUrl] = useState("");
  const [zoom, setZoom] = useState(100);
  const [isExporting, setIsExporting] = useState(false);
  const imageRef = useRef<HTMLImageElement>(null);
  const { user, logout } = useAuth();

  const user_id = localStorage.getItem("userEmail");
  const tenant_id = localStorage.getItem("userName");
  const token = localStorage.getItem('authToken');  

  const [request, setRequest] = useState('https://24h9prbdzc.execute-api.us-east-1.amazonaws.com/dev/erd')

  function getRawGitHubUrl(url: string): string {
    const regex = /^https:\/\/github\.com\/([^/]+)\/([^/]+)\/blob\/([^/]+)\/(.+)$/
    const match = url.match(regex)
    return match
      ? `https://raw.githubusercontent.com/${match[1]}/${match[2]}/${match[3]}/${match[4]}`
      : url
  }

  const diagramTypes: {
    value: DiagramType;
    label: string;
    description: string;
  }[] = [
    { value: "aws", label: "AWS", description: "Amazon Web Services" },
    { value: "json", label: "JSON", description: "Json Diagram (Desarrollo)"},
    { value: "er", label: "E-R", description: "Diagram (Desarrollo)" },
    { value: "generic", label: "Generic", description: "Generic Components" },
  ];
  const API_ENDPOINTS: Record<DiagramType, string> = {
  aws:  'https://dlfz6n75y3.execute-api.us-east-1.amazonaws.com/dev/conversion/aws',
  json: 'https://eaeu5ax03c.execute-api.us-east-1.amazonaws.com/dev/generate-diagram',
  er:   'https://24h9prbdzc.execute-api.us-east-1.amazonaws.com/dev/erd',
  generic: 'https://dlfz6n75y3.execute-api.us-east-1.amazonaws.com/dev/conversion/aws' 
}

  const getPlaceholderCode = (type: DiagramType): string => {
    const placeholders = {
      aws: `from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB

with Diagram("Web Service", show=False):
    lb = ELB("Load Balancer")
    web = EC2("Web Server")
    db = RDS("Database")
    
    lb >> web >> db`,
      er:`CREATE TABLE department (
  id INTEGER PRIMARY KEY,
  name TEXT
);

CREATE TABLE employee (
  id INTEGER PRIMARY KEY,
  name TEXT,
  department_id INTEGER,
  FOREIGN KEY(department_id) REFERENCES department(id)
);

CREATE TABLE project (
  id INTEGER PRIMARY KEY,
  name TEXT
);

CREATE TABLE assignment (
  employee_id INTEGER,
  project_id INTEGER,
  PRIMARY KEY(employee_id, project_id),
  FOREIGN KEY(employee_id) REFERENCES employee(id),
  FOREIGN KEY(project_id) REFERENCES project(id)
);`
      ,
      json:`{
  "Empresa": {
    "Ventas": {
      "Domestic": {},
      "International": {}
    }
  },
  "Ingenieria": {
    "Backend": {
      "API": {},
      "BaseDeDatos": {}
    }
  },
  "Frontend": {},
  "Recursos_Humanos": {
    "Seleccion": {},
    "Formacion": {}
  },
  "Soporte": {}
}` ,
      generic: `from diagrams import Diagram
from diagrams.generic.blank import Blank

with Diagram("Generic Diagram", show=False):
    a = Blank("Component A")
    b = Blank("Component B")
    c = Blank("Component C")
    
    a >> b >> c`,
    };

    return placeholders[type];
  };

  const handleGenerateDiagram = async () => {
    
    if (!code.trim()) {
      toast.error("Por favor, ingresa la definición del diagrama");
      return;
    }

    setIsGenerating(true);
        setIsExporting(true);
    console.log("Enviando datos al backend...");
    console.log({ user_id, tenant_id, code, token });
    try {
      const response = await fetch(request, {
        method: 'POST',
        headers: {
            ...(token ? { 'Authorization': token } : {})
          },
        body: JSON.stringify({
          user_id: user_id,         // ID del usuario
          tenant_id: tenant_id,     // ID del tenant
          code: code           // Código del diagrama que el usuario escribió
        })
      });

      const data = await response.json();

      console.log("Respuesta del backend:");
      console.log(response.body); 
      console.log(response); 
      console.log(data);
      if (response.ok) {
        toast.success("Datos enviados correctamente al backend.");
      } else {
        toast.error("Hubo un problema al enviar los datos.");
      }

      setGeneratedImageUrl(data.imageUrl);
      console.log("URL de la imagen generada:", response.url);
      toast.success("¡Diagrama generado correctamente!");

    } catch (error) {
      toast.error("Error al hacer la solicitud al backend.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleLoadFromGithub = useCallback(async () => {
    if (!githubUrl.trim()) {
      toast.error('Por favor pega una URL de GitHub válida')
      return
    }
    //setIsLoadingUrl(true)
    try {
      const rawUrl = getRawGitHubUrl(githubUrl.trim())
      const resp = await fetch(rawUrl)
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const text = await resp.text()
      setCode(text)
      toast.success('Código cargado desde GitHub')
    } catch (err) {
      console.error(err)
      toast.error('No se pudo cargar el archivo desde esa URL')
    } finally {
      //setIsLoadingUrl(false)
    }
  }, [githubUrl])

  const handleFileUpload = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (!file) return

      // opcional: validar extensión
      const ext = file.name.split('.').pop()?.toLowerCase()
      if (!['txt', 'py'].includes(ext!)) {
        alert('Solo se permiten .txt o .py')
        return
      }

      try {
        const text = await file.text()   // lee todo como string
        setCode(text)                    // vuelca al textarea/editor
      } catch (err) {
        console.error(err)
        alert('Error leyendo el archivo')
      }
    },
    []
  )

  // Export functions
  const handleExportSVG = async () => {
    if (!generatedImageUrl) return;

    setIsExporting(true);
    try {
      const response = await fetch(generatedImageUrl);
      const blob = await response.blob();
      saveAs(blob, `diagram-${diagramType}-${Date.now()}.svg`);
      toast.success("Diagrama SVG descargado correctamente");
    } catch {
      toast.error("Error al descargar el diagrama SVG");
    } finally {
      setIsExporting(false);
    }
  };

  const handleExportPNG = async () => {
    if (!imageRef.current) return;

    if (!generatedImageUrl) {
      toast.error("No hay imagen generada para descargar")
      return
    }

    setIsExporting(true)
    try {
      const res = await fetch(generatedImageUrl, { mode: 'cors' })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const blob = await res.blob()
      saveAs(blob, `diagram-${diagramType}-${Date.now()}.png`)
      toast.success('Descarga completada')
    } catch (err) {
      console.error(err)
      toast.error('Error al descargar desde S3')
    } finally {
      setIsExporting(false)
    }


    try {
      const canvas = await html2canvas(imageRef.current, {
        backgroundColor: "#ffffff",
        scale: 2,
        useCORS: true,
      });

      canvas.toBlob((blob) => {
        if (blob) {
          saveAs(blob, `diagram-${diagramType}-${Date.now()}.png`);
          toast.success("Diagrama PNG descargado correctamente");
        }
        setIsExporting(false);
      }, "image/png");
    } catch {
      toast.error("Error al descargar el diagrama PNG");
      setIsExporting(false);
    }
  };

  const handleExportPDF = async () => {
    if (!imageRef.current) return;

    setIsExporting(true);
    try {
      const canvas = await html2canvas(imageRef.current, {
        backgroundColor: "#ffffff",
        scale: 2,
        useCORS: true,
      });

      const imgData = canvas.toDataURL("image/png");
      const pdf = new jsPDF({
        orientation: canvas.width > canvas.height ? "landscape" : "portrait",
        unit: "px",
        format: [canvas.width, canvas.height],
      });

      pdf.addImage(imgData, "PNG", 0, 0, canvas.width, canvas.height);
      pdf.save(`diagram-${diagramType}-${Date.now()}.pdf`);
      toast.success("Diagrama PDF descargado correctamente");
    } catch {
      toast.error("Error al descargar el diagrama PDF");
    } finally {
      setIsExporting(false);
    }
  };

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 25, 200));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 25, 25));
  const handleResetZoom = () => setZoom(100);

  React.useEffect(() => {
    console.log('El usuario seleccionó el tipo:', diagramType)
    setCode(getPlaceholderCode(diagramType))
    const url = API_ENDPOINTS[diagramType] || ''
    setRequest(url) 
    console.log(request)
    
  }, [diagramType])

  const handleTypeChange = (newType: DiagramType) => {
    setDiagramType(newType);            
  }


  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          {" "}
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-gray-900">
              Diagram Generator
            </h1>
            <span className="text-sm text-gray-500">
              Powered by Diagrams.py
            </span>
            <span className="text-xs text-blue-600 font-medium">
              • Creado por "Todo va a estar Bien"
            </span>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">
              Bienvenido, {user?.name}
            </span>
            <button
              onClick={logout}
              className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
            >
              <LogOut size={16} />
              <span>Cerrar Sesión</span>
            </button>
          </div>
        </div>
      </header>

      <div className="flex-1 flex">
        {/* Left Panel - Editor */}
        <div className="w-1/2 flex flex-col bg-white border-r border-gray-200">
          {/* Controls */}
          <div className="p-4 border-b border-gray-200 space-y-4">
            {/* Diagram Type Selector */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tipo de Diagrama
              </label>
              <select
                value={diagramType}
                onChange={(e) =>
                  handleTypeChange(e.target.value as DiagramType)
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {diagramTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label} - {type.description}
                  </option>
                ))}
              </select>
            </div>

            {/* GitHub URL Input */}
            <div className="flex space-x-2">
              <input
                type="url"
                placeholder="URL del archivo Python en GitHub..."
                value={githubUrl}
                onChange={(e) => setGithubUrl(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleLoadFromGithub}
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 flex items-center space-x-2"
              >
                <Github size={16} />
                <span>Cargar</span>
              </button>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-2">
              <button
                onClick={handleGenerateDiagram}
                disabled={isGenerating || !code.trim()}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Play size={16} />
                <span>
                  {isGenerating ? "Generando..." : "Generar Diagrama"}
                </span>
              </button>

              <label className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 cursor-pointer">
                <Upload size={16} />
                <span>Subir Archivo</span>
                <input
                  type="file"
                  accept=".py,.txt"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </label>
            </div>
          </div>

          {/* Monaco Editor */}
          <div className="flex-1">
            <Editor
              height="100%"
              defaultLanguage="python"
              value={code}
              onChange={(value) => setCode(value || "")}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                fontSize: 14,
                lineNumbers: "on",
                wordWrap: "on",
                automaticLayout: true,
              }}
            />
          </div>
        </div>

        {/* Right Panel - Preview */}
        <div className="w-1/2 flex flex-col bg-gray-50">
          {/* Preview Controls */}
          <div className="p-4 bg-white border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">
                Vista Previa
              </h3>
              <div className="flex items-center space-x-2">
                {generatedImageUrl && (
                  <>
                    <button
                      onClick={handleExportSVG}
                      //disabled={isExporting}
                      className="flex items-center space-x-2 px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <ImageIcon size={16} />
                      <span>{isExporting ? "Exportar" : "SVG"}</span>
                    </button>

                    <button
                      onClick={handleExportPNG}
                      //disabled={isExporting}
                      className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <FileImage size={16} />
                      <span>{isExporting ? "Exportar" : "PNG"}</span>
                    </button>

                    <button
                      onClick={handleExportPDF}
                      //disabled={isExporting}
                      className="flex items-center space-x-2 px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <FilePdf size={16} />
                      <span>{isExporting ? "Exportar" : "PDF"}</span>
                    </button>
                  </>
                )}
                <div className="flex items-center space-x-1 border border-gray-300 rounded-md">
                  <button
                    onClick={handleZoomOut}
                    className="p-2 hover:bg-gray-100"
                    disabled={zoom <= 25}
                  >
                    <ZoomOut size={16} />
                  </button>
                  <span className="px-2 text-sm font-medium min-w-[60px] text-center">
                    {zoom}%
                  </span>
                  <button
                    onClick={handleZoomIn}
                    className="p-2 hover:bg-gray-100"
                    disabled={zoom >= 200}
                  >
                    <ZoomIn size={16} />
                  </button>
                  <button
                    onClick={handleResetZoom}
                    className="p-2 hover:bg-gray-100 border-l border-gray-300"
                  >
                    <RotateCcw size={16} />
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Preview Content */}
          <div className="flex-1 overflow-auto p-4">
            {isGenerating ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">Generando diagrama...</p>
                </div>
              </div>
            ) : generatedImageUrl ? (
              <div className="flex justify-center">
                <img
                  ref={imageRef}
                  src={generatedImageUrl}
                  alt="Generated Diagram"
                  style={{ transform: `scale(${zoom / 100})` }}
                  className="max-w-none transition-transform duration-200"
                />
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                <div className="text-center">
                  <FileText size={48} className="mx-auto mb-4 text-gray-300" />
                  <p>
                    Escribe tu código Python y haz clic en "Generar Diagrama"
                  </p>
                  <p className="text-sm mt-2">
                    Usa la biblioteca Diagrams.py para crear diagramas de
                    arquitectura
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiagramEditor;
