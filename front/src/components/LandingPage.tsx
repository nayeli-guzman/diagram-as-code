import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import {
  Network,
  Code,
  Zap,
  Shield,
  Download,
  Github,
  ChevronRight,
  Star,
} from "lucide-react";

const LandingPage: React.FC = () => {
  const { isAuthenticated, user } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100">
      {/* Header */}
      <header className="px-6 py-4 bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {" "}
            <Network className="h-8 w-8 text-blue-600" />
            <span className="text-xl font-bold text-gray-900">DiagramCode</span>
          </div>
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600">
                  Bienvenido
                </span>
                <Link
                  to="/editor"
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Ir al Editor
                </Link>
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <Link
                  to="/login"
                  className="text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Iniciar Sesión
                </Link>
                <Link
                  to="/signup"
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Registrarse
                </Link>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="px-6 py-20">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Diagramas de Arquitectura
            <span className="block text-blue-600">Como Código</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Crea diagramas profesionales de infraestructura y arquitectura
            usando Python y Diagrams.py. Código versionable, reproducible y
            colaborativo.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            {isAuthenticated ? (
              <Link
                to="/editor"
                className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center"
              >
                Comenzar a Crear
                <ChevronRight className="ml-2 h-5 w-5" />
              </Link>
            ) : (
              <>
                <Link
                  to="/signup"
                  className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center"
                >
                  Comenzar Gratis
                  <ChevronRight className="ml-2 h-5 w-5" />
                </Link>
                <Link
                  to="/login"
                  className="border-2 border-blue-600 text-blue-600 px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-600 hover:text-white transition-colors"
                >
                  Iniciar Sesión
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="px-6 py-16 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Características Principales
            </h2>
            <p className="text-lg text-gray-600">
              Todo lo que necesitas para crear diagramas profesionales
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Code className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Editor Monaco</h3>
              <p className="text-gray-600">
                Editor de código profesional con syntax highlighting,
                autocompletado y validación en tiempo real.
              </p>
            </div>

            <div className="text-center p-6">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Zap className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">
                Múltiples Providers
              </h3>
              <p className="text-gray-600">
                Soporte para AWS, Azure, GCP, Kubernetes, redes y más. Todos los
                providers de Diagrams.py.
              </p>
            </div>

            <div className="text-center p-6">
              <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">
                Autenticación Segura
              </h3>
              <p className="text-gray-600">
                Sistema de autenticación con JWT, sesiones persistentes y rutas
                protegidas.
              </p>
            </div>

            <div className="text-center p-6">
              <div className="bg-yellow-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Download className="h-8 w-8 text-yellow-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Exportación Fácil</h3>
              <p className="text-gray-600">
                Descarga tus diagramas en formatos SVG, PNG o PDF con un solo
                clic.
              </p>
            </div>

            <div className="text-center p-6">
              <div className="bg-red-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Github className="h-8 w-8 text-red-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Integración GitHub</h3>
              <p className="text-gray-600">
                Carga archivos directamente desde repositorios de GitHub para
                editar y versionar.
              </p>
            </div>

            <div className="text-center p-6">
              {" "}
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Star className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">
                Vista Previa Interactiva
              </h3>
              <p className="text-gray-600">
                Visualización en tiempo real con zoom, scroll y controles
                interactivos.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Code Example */}
      <section className="px-6 py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Simple Como Escribir Código
            </h2>
            <p className="text-lg text-gray-600">
              Escribe Python, obtén diagramas profesionales
            </p>
          </div>

          <div className="bg-gray-900 rounded-lg p-6 text-green-400 font-mono text-sm overflow-x-auto">
            <pre>{`from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB

with Diagram("Web Service", show=False):
    lb = ELB("Load Balancer")
    web = EC2("Web Server") 
    db = RDS("Database")
    
    lb >> web >> db`}</pre>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 py-20 bg-blue-600">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            ¿Listo para crear tus primeros diagramas?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Únete a desarrolladores que ya están creando documentación visual de
            alta calidad
          </p>
          {!isAuthenticated && (
            <Link
              to="/signup"
              className="bg-white text-blue-600 px-8 py-3 rounded-lg text-lg font-semibold hover:bg-gray-100 transition-colors inline-flex items-center"
            >
              Comenzar Ahora
              <ChevronRight className="ml-2 h-5 w-5" />
            </Link>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 py-8 bg-gray-900 text-gray-400">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Network className="h-6 w-6 text-blue-400" />
            <span className="text-lg font-semibold text-white">
              DiagramCode
            </span>
          </div>{" "}
          <p className="text-sm">
            Powered by Diagrams.py • Built with React + TypeScript + Tailwind
          </p>
          <p className="text-xs mt-2 text-blue-400">
            ❤️ Creado con amor por el grupo{" "}
            <span className="font-semibold">"Todo va a estar Bien"</span>
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
