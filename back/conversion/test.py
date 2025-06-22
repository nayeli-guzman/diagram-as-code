import graphviz

# Prueba si Graphviz se puede ejecutar
try:
    print("Probando Graphviz")
    dot = graphviz.Digraph(comment='Test')
    dot.node('A', 'Inicio')
    dot.node('B', 'Fin')
    dot.edge('A', 'B', 'A -> B')
    print("Diagrama generado correctamente con Graphviz")
    dot.render('/tmp/test_diagram', format='png')  # Intenta renderizar el diagrama
except Exception as e:
    print(f"Error al usar Graphviz: {str(e)}")
