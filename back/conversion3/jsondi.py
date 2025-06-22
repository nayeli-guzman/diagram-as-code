#!/usr/bin/env python3
"""
Generador de Diagramas de Estructura JSON
Este script genera diagramas visuales de estructuras JSON usando Graphviz.
"""

import json
from graphviz import Digraph

def generar_estructura_ecommerce():
    """Genera un diagrama de estructura JSON simple para un sistema de ecommerce"""
    
    data = {
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
    
    return data

def generar_estructura_universidad():
    """Genera un diagrama de estructura JSON para un sistema universitario"""
    
    data = {
        "Universidad": {
            "Estudiantes": {
                "Pregrado": {
                    "Ingenieria": {"sistemas": {}, "civil": {}, "industrial": {}},
                    "Medicina": {"general": {}, "odontologia": {}},
                    "Humanidades": {"psicologia": {}, "derecho": {}}
                },
                "Postgrado": {
                    "Maestrias": {"mba": {}, "educacion": {}},
                    "Doctorados": {"investigacion": {}, "ciencias": {}}
                }
            },
            "Personal": {
                "Academico": {
                    "Profesores": {"tiempo_completo": {}, "catedra": {}},
                    "Investigadores": {"junior": {}, "senior": {}}
                },
                "Administrativo": {
                    "Direccion": {"rectoria": {}, "vicerrectorias": {}},
                    "Servicios": {"biblioteca": {}, "laboratorios": {}}
                }
            },
            "Academico": {
                "Facultades": {
                    "Ingenieria": {"departamentos": {}, "laboratorios": {}},
                    "Medicina": {"clinicas": {}, "residencias": {}},
                    "Humanidades": {"centros_investigacion": {}}
                },
                "Programas": {
                    "Curriculares": {"materias": {}, "practicas": {}},
                    "Extracurriculares": {"deportes": {}, "cultura": {}}
                }
            }
        }
    }
    
    return data

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

def generar_diagrama_json(data, filename, title):
    """Genera y guarda un diagrama JSON"""
    
    print(f"📊 Generando {title}...")
    graph = json_to_graph(data)
    graph.attr(label=title, fontsize='18', fontweight='bold')
    graph.render(filename, format='png', cleanup=True)
    print(f"✅ Diagrama guardado: {filename}.png")

def mostrar_estructura_texto(data, indent=0):
    """Muestra la estructura JSON como texto indentado"""
    
    for key, value in data.items():
        print("  " * indent + f"├── {key}")
        if isinstance(value, dict) and value:
            mostrar_estructura_texto(value, indent + 1)
        elif isinstance(value, dict) and not value:
            print("  " * (indent + 1) + "└── (vacío)")

def main():
    print("📈 Generando Diagrama Simple de Estructura JSON...")
    
    # Generar solo el diagrama de ecommerce simplificado
    data_ecommerce = generar_estructura_ecommerce()
    generar_diagrama_json(data_ecommerce, "json_tienda_simple", "Estructura JSON - Tienda Online Simple")
    
    print("\n📊 Diagrama generado:")
    print("- json_tienda_simple.png (Estructura básica de tienda online)")
    
    print("\n🏗️ Estructura de la Tienda:")
    mostrar_estructura_texto(data_ecommerce)
    
    print("\n💡 Este diagrama muestra:")
    print("• Estructura básica de una tienda online")
    print("• Jerarquía simple de datos")
    print("• 3 módulos principales: Usuarios, Productos, Pedidos")
    print("• Fácil de entender y modificar")

if __name__ == '__main__':
    main()
