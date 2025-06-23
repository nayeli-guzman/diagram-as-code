import json
import base64
import io
import tempfile
import os
from datetime import datetime
import uuid
from graphviz import Digraph

def json_to_graph(data, graph=None, parent=None, level=0):
    if graph is None:
        graph = Digraph(comment='Estructura JSON')
        graph.attr(rankdir='TB')
        graph.attr('node', shape='rectangle', style='rounded,filled')
        graph.attr('edge', color='#666666')
    
    colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightcoral', 'lightpink', 'lightgray']
    color = colors[min(level, len(colors)-1)]
    
    for key, value in data.items():
        node_id = f"{parent}_{key}" if parent else key

        if level == 0:
            graph.node(node_id, f"🏢 {key}", fillcolor=color, fontsize='16', fontweight='bold')
        elif level == 1:
            graph.node(node_id, f"📁 {key}", fillcolor=color, fontsize='14', fontweight='bold')
        elif level == 2:
            graph.node(node_id, f"📂 {key}", fillcolor=color, fontsize='12')
        else:
            graph.node(node_id, f"📄 {key}", fillcolor=color, fontsize='10')
        
        if parent:
            graph.edge(parent, node_id)
        
        if isinstance(value, dict) and value:
            json_to_graph(value, graph, node_id, level + 1)
        elif isinstance(value, dict) and not value:
            empty_id = f"{node_id}_empty"
            graph.node(empty_id, "📋 (vacío)", shape='ellipse', fillcolor='white', fontsize='8')
            graph.edge(node_id, empty_id, style='dashed', color='lightgray')
    
    return graph

def generate_random():
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

code = generate_random()
filepath = "tmp/diagrama"
graph = json_to_graph(code)
graph.attr(label="a", fontsize='18', fontweight='bold')
graph.render(filepath, format='png', cleanup=True)
            