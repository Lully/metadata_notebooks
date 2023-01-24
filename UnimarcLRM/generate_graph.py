# coding: utf-8

explain = """Génération de graphes en SVG 
             à intégrer aux pages de résultats HTML (en pied de page)"""

import os
import graphviz

def generate_graph_from_oeuvre(oeuvre, dict_entities, size):
    # A partir d'une manifestation, renvoie un graphe GraphViz
    dot = graphviz.Digraph(oeuvre.id, comment=f'Notice {oeuvre.id}')  
    dot.attr(rankdir='LR')
    dot.attr(size=size)
    # Add nodes and edges to the graph object using its node() and edge() or edges() methods:
    dot.node(oeuvre.id, oeuvre.label)
    dot.format = "svg"
    liste_edges = []
    for expr in oeuvre.toExpressions:
        if expr:
            dot.node(expr, dict_entities[expr].label)
            dot.edge(expr, oeuvre.id, label="Expression de")
        for manif in dict_entities[expr].toManifs:
            if manif:
                dot.node(manif, dict_entities[manif].label)
                dot.edge(manif, expr, label="Manifestation de")
    dot.render(directory='results/graphs').replace('\\', '/')
 
    return dot
    # dot.edges(liste_edges)
    
def oeuvreid2graph(record, dict_entities, size="10,10"):
    graph = generate_graph_from_oeuvre(record, dict_entities, size)
    return graph
