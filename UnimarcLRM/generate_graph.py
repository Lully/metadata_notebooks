# coding: utf-8

explain = """Génération de graphes en SVG 
             à intégrer aux pages de résultats HTML (en pied de page)"""

import os
import graphviz

def generate_graph_from_oeuvre(entity, dict_entities, size, shape="rect"):
    # A partir d'une manifestation, renvoie un graphe GraphViz
    dot = graphviz.Digraph(entity.id, comment=f'Notice {entity.id}')  
    # dot.attr(rankdir='LR')
    dot.attr(size=size)
    dot.attr(rankdir="BT")
    dot.node_attr['shape'] = shape
    
    #dot.node_attr['color'] = "red"
    dot.node_attr['align'] = "left"
    #dot.node_attr['width'] = "300px"
    # Add nodes and edges to the graph object using its node() and edge() or edges() methods:
    dot.node(entity.id, entity.splitted_label, color="red")
    dot.format = "svg"
    liste_edges = []
    if entity.type == "o":
        for expr in entity.toExpressions:
            if expr:
                dot.node(expr, dict_entities[expr].splitted_label)
                dot.edge(expr, entity.id, label="Expression de")
            for manif in dict_entities[expr].toManifs:
                if manif:
                    dot.node(manif, dict_entities[manif].splitted_label)
                    dot.edge(manif, expr, label="Manifestation de")
    elif entity.type == "e":
        for oeuvre in entity.toOeuvres:
            if oeuvre:
                dot.node(oeuvre, dict_entities[oeuvre].splitted_label)
                dot.edge(entity.id, oeuvre, label="Expression de")
        for manif in entity.toManifs:
            if manif:
                dot.node(manif, dict_entities[manif].splitted_label)
                dot.edge(manif, entity.id, label="Manifestation de")

    dot.render(directory='results/graphs').replace('\\', '/')
 
    return dot
    # dot.edges(liste_edges)
    
def oeuvreid2graph(record, dict_entities, size="10,10"):
    graph = generate_graph_from_oeuvre(record, dict_entities, size)
    return graph
