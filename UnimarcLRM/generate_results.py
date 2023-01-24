# coding: utf-8

import os
from unidecode import unidecode
from lxml.html import parse
from lxml import etree
from common_dicts import *

from random import choice

from generate_graph import oeuvreid2graph

def clean_str(string):
    string = unidecode(string.lower())
    punct = "!:,;.?/%$\"'"
    for char in punct:
        string = string.replace("char", " ")
    string = " ".join([el for el in string.split(" ") if el])
    return string


def search(keywords, oeuvres, dict_entities, index="all"):
    keywords = clean_str(keywords).split(" ")
    results_entities = {}
    for o in oeuvres:
        if index == "all":
            for k in keywords:
                if k in o.global_index:
                    results_entities[o.id] = o
    return results_entities


def display_html_results(dict_results, dict_entities, query):
    # A partir d'un lot de notices d'oeuvres comme résultats d'une recherche
    # cette fonction génère 
    #       une page "results/short_results.html"  avec la liste des résultats (abrégés)
    #       et une page "results/full_results_0.html" qui pour chaque résultat génère une page HTML numérotée 
    short_html = generate_short_results_html(dict_results, dict_entities, query) # renvoie le code HTML
    full_html = generate_full_results_html(dict_results, dict_entities, query)   # renvoie une liste de code HTML


def generate_short_results_html(dict_results, dict_entities, query):
    file = open("results/short_results.html", "w", encoding="utf-8")
    write_html_head(file, "Liste de résultats")
    write_html_short_body(file, dict_results, query)
    write_html_footer(file)


def generate_full_results_html(dict_results, dict_entities, query):
    # Génération de toutes les pages HTML de notices détaillées
    i = 1
    for result in dict_results:
        file = open(f"results/full_results_{result}.html", "w", encoding="utf-8")
        write_html_head(file, f"Notice détaillée {dict_results[result].label}")
        write_html_full_body(file, result, dict_results[result], query, i, dict_entities)
        write_html_footer(file)
        i += 1


def write_html_short_body(file, dict_results, query):
    file.write("<body>")
    file.write(generate_entete(query))

    i = 1
    for r in dict_results:
        file.write(f"<p>{str(i)}. <a href='full_results_{r}.html'>{dict_results[r].label}</a></p>")
        i += 1
    file.write("</body>")

def write_html_full_body(file, recordid, record, query, i, dict_entities):
    # Génération d'une page de notice détaillée
    file.write("\n<body>\n")
    file.write(generate_entete(query, i))
    file.write(f"\n<p>{record.detailed}</p>")

    # ----------------------- #
    #    Les filtres          #
    # ----------------------- #
    filters = generate_work_filters(record)
    file.write(f"\n<div class='filters'>{filters}</div>")

    # ------------------------#
    #    Les exemplaires      #
    # ------------------------#
    div_items = generate_html_items(record, dict_entities)
    file.write(f"\n<div class='items'>{div_items}</div>\n")


    # ------------------------#
    #   Les infos pro         #
    # ------------------------#
    div_infos_pro = generate_pro_infos(recordid, record, dict_entities)
    file.write(f"\n<div class='pro'>{div_infos_pro}</div>\n")

    file.write("\n</body>\n")


def generate_html_items(record, dict_entities):
    dict_states = {"d": "Disponible", "e": "Emprunté"}
    dict_class = {"d": "avail", "e": "unavail"}
    list_items = []
    for item in record.toItems:
        if item:
            state = choice(list(dict_states))
            state_label = dict_states[state]
            full_item = dict_entities[item]
            expr = dict_entities[item].toExpressions
            expr_labels = []
            for e in expr:
                expr_labels.append(expr[e])
            expr_labels = " - ".join(expr_labels)
            desc_item = f"{state_label} - {expr_labels} - {full_item.localisation} {full_item.cote}"
            html_item = f"<p class='{dict_class[state]}'>{desc_item}</p>"
            list_items.append(html_item)
    div_items = "<h3>Liste des exemplaires</h3>\n"
    div_items += "\n".join(list_items)
    return div_items


def generate_pro_infos(recordid, record, dict_entities):
    # Renvoi d'un ensemble d'infos professionnelles
    infos_pro = "<hr/>\n<h3>Infos professionnelles</h3>"
    infos_pro += f"\n<div class='recordid'><p class='recordid'>{recordid}</p><//div>\n"

    graph = oeuvreid2graph(record, dict_entities, size="20,20")
    svg_graph = f"graphs/{recordid}.gv.svg"
    # div_graph = f'<a target="blank" href="{svg_graph}" title="Afficher le graphe"><img src = "{svg_graph}" alt="Graphe de l\'oeuvre"/>'
    div_graph = f'\n<div class="graph">{graphfilename2content(svg_graph)}</div>\n'
    infos_pro += div_graph
    return f'\n{infos_pro}\n'
    
def graphfilename2content(graphfilename):
    svg_content = etree.parse(os.path.join("results", graphfilename))
    svg_content = svg_content.xpath("//s:svg", namespaces={"s": "http://www.w3.org/2000/svg"})[0]
    svg_content = etree.tostring(svg_content).decode("utf-8")
    return svg_content

def generate_work_filters(record):
    # A partir d'une notice d'oeuvre, générer une liste de liens
    # (<a href=''>) permettant de gérer des filtres
    
    # Première ligne de filtres (moteur de recherche, langues, dates)
    header = "<h3>Filtres</h3>"
    filter_form = "<input type='form' width='150px' value='Limiter les résultats'/>"
    filters_lng = ""
    for lang in record.lang:
        try:
            link = f'<a class="filters_lng" href="#">{dict_lang2label[lang]}</a>'
        except KeyError:
            link = f'<a class="filters_lng" href="#">{lang}</a>'
        filters_lng += f" {link}"
    filters_content_type = []
    for expr_content_type in record.exprContentType:
        link = f'<a class="filters_content_type" href="#">{expr_content_type}</a>'
        filters_content_type.append(link)
    filters_content_type = " ".join(filters_content_type)
    filters_elements = [filter_form, filters_lng, filters_content_type]
    filters1 = f"<div class='filters1'>{' '.join(filters_elements)}</div>"

    # Deuxième ligne (mentions de responsabilités des expressions)
    links_resp = []
    for resp in record.exprResp:
        link = f'<a href="#">{resp}</a>'
        links_resp.append(link)
    links_resp = " | ".join(links_resp)
    filters2 = f"<div class='filters2'>{links_resp}</div>"
    return "\n".join([header, filters1, filters2])


def generate_entete(query, no_resultat=0):
    entete = '\n<div class="entete">'
    entete += f'\n<p>Rappel de la recherche : <strong>{query}</strong></p>'
    if no_resultat:
        entete += "\n<p class='back'><a href='short_results.html'>Retour à la liste des résultats</a></p>"
        entete += f'<h1>Résultat {str(no_resultat)}</h1>'
    else:
        entete += "<h1>Liste des résultats</h1>"
    entete += "</div>"
    return entete


def write_html_head(file, html_title):
    file.write(f"<html>\n<head>\n<meta charset='UTF-8'>\n<title>{html_title}</title>\n\
<link rel='stylesheet' href='../styles.css'/>")
    with open("styles.css", "r", encoding="utf-8") as cssfile:
        file.write("<style type='text/css'>")
        for row in cssfile.readlines():
            file.write(row)
        file.write("</style>")
    file.write("</head>")


def write_html_footer(file):
    file.write("</html>")
        
def delete_html_results():
    for filename in os.listdir("results"):
        if ".html" in filename:
            os.remove(f"results/{filename}")
    for filename  in os.listdir("results/graphs"):
            os.remove(f"results/graphs/{filename}")
