# coding: utf-8

import os
import json
from unidecode import unidecode
import collections
from lxml.html import parse
from lxml import etree
from common_dicts import *

from random import choice

from Record import html_label
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


def display_html_results(dict_results, dict_entities, query, type_entity):
    # A partir d'un lot de notices d'oeuvres comme résultats d'une recherche
    # cette fonction génère 
    #       une page "results/short_results.html"  avec la liste des résultats (abrégés)
    #       et une page "results/full_results_0.html" qui pour chaque résultat génère une page HTML numérotée 
    short_html = generate_short_results_html(dict_results, dict_entities, query, type_entity) # renvoie le code HTML
    full_html = generate_full_results_html(dict_results, dict_entities, query, type_entity)   # renvoie une liste de code HTML


def generate_short_results_html(dict_results, dict_entities, query, type_entity):
    file = open(f"results/short_results_{type_entity}.html", "w", encoding="utf-8")
    write_html_head(file, "Liste de résultats", type_entity)
    write_html_short_body(file, dict_results, query, type_entity)
    write_html_footer(file)


def generate_full_results_html(dict_results, dict_entities, query, type_entity):
    # Génération de toutes les pages HTML de notices détaillées
    i = 1
    for result in dict_results:
        file = open(f"results/full_results_{result}.html", "w", encoding="utf-8")
        write_html_head(file, f"Notice détaillée {dict_results[result].label}", type_entity)
        write_html_full_body(file, result, dict_results[result], query, i, dict_entities)
        write_html_footer(file)
        generate_json_file(result, dict_results[result])
        if type_entity == "e":
            # Si type d'entité = expression : générer les listes de résultats pour toutes les versions d'une oeuvre
            generate_list_all_expressions(dict_results[result], dict_entities)
        i += 1


def generate_list_all_expressions(result, dict_entities):
    # A partir d'une entité Expression, 
    # générer une liste de résultats présentant toutes les autres expressions
    # de la même oeuvre
    oid = "".join(list(result.toOeuvres))  # Oeuvre de l'expression de départ
    dict_other_expressions = {}
    for eid in dict_entities[oid].toExpressions:
        dict_other_expressions[eid] = dict_entities[eid]
    
    file = open(f"results/short_results_{oid}_e.html", "w", encoding="utf-8")
    write_html_head(file, "Liste de résultats", "e")
    write_html_short_body(file, dict_other_expressions, 
                          f"Liste des versions de : {dict_entities[oid].label}", 
                          "e")
    write_html_footer(file)


def generate_json_file(recordid, record):
    json_record = {}
    for key in record.__dict__:
        json_record[key] = record.__dict__[key]
    for key in json_record:
        if type(json_record[key]) == etree._Element:
            json_record[key] = etree.tostring(json_record[key]).decode("utf-8")
        if isinstance(json_record[key], collections.defaultdict):
            json_record[key] = dict(json_record[key])
        if isinstance(json_record[key], set):
            json_record[key] = list(json_record[key])
        if isinstance(json_record[key], bytes):
            json_record[key] = json_record[key].decode("utf-8")
    json_record = json.dumps(json_record, indent=4)
    with open(f"results/{recordid}.json", "w", encoding="utf-8") as json_file:
        json_file.write(json_record)

def write_html_short_body(file, dict_results, query, type_entity):
    file.write(f"<body class='{type_entity}'>")
    file.write(generate_entete(query, type_entity, 0))

    i = 1
    for r in dict_results:
        if type_entity == "o":
            one_result = work_short_result(i, r, dict_results[r])
        elif type_entity == "e":
            one_result = expression_short_result(i, r, dict_results[r])
        file.write(one_result)
        i += 1
    file.write("</body>")

def work_short_result(i, entity_id, record):
    # Une notice abrégée pour liste de résultats -- oeuvres
    short_result = f"<p>{str(i)}. <a class='short_result_work' href='full_results_{entity_id}.html'>{record.label}</a><br/>"
    version_word = ["version", "versions"][len(record.toExpressions) > 1]
    icons_content_type = " ".join([get_icon_content_type(e) for e in record.exprContentType])
    short_result += '<span class="short_result_details">'
    short_result += icons_content_type
    short_result += f'{str(len(record.toExpressions))} {version_word} de cette oeuvre</span>'
    short_result += "</p>"
    return short_result

def get_icon_content_type(expression_content_type):
    html_img = f'<img alt="[{expression_content_type}] " title="{expression_content_type}" src="icons/{expression_content_type}.png"/>'
    return html_img

def expression_short_result(i, entity_id, record):
    # Une notice abrégée pour liste de résultats -- expressions
    short_result = f"<p>{str(i)}. <a class='short_result_expression' href='full_results_{entity_id}.html'>{record.label}</a>"
    short_result += "<br/>"
    short_result += '<span class="short_result_details">'
    for oeuvreid in record.toOeuvres:
        short_result += f'<a class="link2work" href="full_results_{oeuvreid}.html">Voir l\'oeuvre et toutes ses versions</a><br/>'
    short_result += "</span>"
    short_result += "</p>"
    return short_result



def write_html_full_body(file, recordid, record, query, i, dict_entities):
    # Génération d'une page de notice détaillée
    file.write(f"\n<body class='{record.type}'>\n")
    file.write(generate_entete(query, record.type, i))
    record_detailed = record.detailed.replace("\n", "<br/>")
    file.write("<div class='full_record'>")
    file.write(f"\n<p class='detailed label'>{record.label}</p>")
    file.write(f"\n<div class='detailed'><p class='detailed'>{record_detailed}</p></div>")
    if record.type == "e":
        record_detailed_sup_replace = record.detailed_sup.replace('\n', '<br/>')
        file.write(f"\n<div class='detailed_sup'><p class='detailed'>{record_detailed_sup_replace}</p></div>")
    
    
    # ----------------------- #
    #    Les rebonds          #
    # ----------------------- #
    record_rebonds = record.rebonds.replace("\n", "</li><li>")
    record_others_expr = record.other_expressions

    
    file.write(f"\n<div class='rebonds'>")
    if record_rebonds:
        file.write(f"<p class='rebonds'><p><strong>Voir aussi</strong></p><ul><li>{record_rebonds}</li></ul>")
    if record.toOeuvres and record.type == "e":
        nb_versions = 0
        for oid in record.toOeuvres:
            nb_versions += len(dict_entities[oid].toExpressions)
            if nb_versions > 1:
                file.write(f"<p><a class='expr2oeuvre_link' href='short_results_{list(record.toOeuvres)[0]}_e.html'>Voir les {str(nb_versions)} versions de l'oeuvre<br>\
<em><strong>{' - '.join(record.toOeuvres.values())}</strong></em></a></p>")
    file.write("</div>")

    # print(recordid, "record.detailed", record.detailed)
    # ----------------------- #
    #    Les filtres          #
    # ----------------------- #
    filters = generate_work_filters(record)
    file.write(f"\n<div class='filters'>{filters}</div>")


    # ------------------------#
    #    Les exemplaires      #
    # ------------------------#
    div_items = generate_html_items(record, dict_entities)
    file.write(f"\n{div_items}\n")

    # ------------------------#
    #    Rebonds vers         #
    #    d'autres oeuvre      #
    # ------------------------#
    if record_others_expr:
        file.write("\n<div class='other_expressions'>\n<p>Autres oeuvres en lien\n")
        file.write("<p class='comment'>Sur une page d'expression, cette rubrique liste directement les expressions des oeuvres liées à l'oeuvre de l'expression en cours</p>")
        file.write("<ul>")
        for expr in record_others_expr:
            expr_label = html_label(record_others_expr[expr])
            expr_label = record_others_expr[expr]
            line = f'<li><a href="full_results_{expr}.html">{expr_label}</a></li>\n'
            file.write(line)
        file.write("</ul>\n</div>")


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
    div_items = "<div class='items'>\n<h3>Liste des exemplaires</h3>\n"
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
            html_item = f"<div class='item'><p class='{dict_class[state]}'>{desc_item}<br/>"
            html_item += item2metassup(item, record, dict_entities)
            html_item += "</p></div>"
            list_items.append(html_item)
    div_items += "\n".join(list_items)
    div_items += "\n</div>\n"
    return div_items


def item2metassup(item, record, dict_entities):
    # Métadonnées biblio raccrochées à chaque item
    manifid = list(dict_entities[item].toManifs)[0]
    manif = dict_entities[manifid]
    metas = {"Titre": manif.title,
             "Edition": manif.publisher,
             "Description": manif.description}
    metas = "<br/>".join([f"{el}: {metas[el]}" for el in metas if metas[el]])
    metas = f"<div class='item2metassup'>{metas}</div>"
    return metas


def generate_pro_infos(recordid, record, dict_entities):
    # Renvoi d'un ensemble d'infos professionnelles
    infos_pro = "<hr/>\n<h3>Infos professionnelles</h3>"
    infos_pro += f"\n<div class='recordid'><p class='recordid'>{recordid} - {record.type}</p></div>\n"
    infos_pro += f"\n<p><a href='{recordid}.json'>Version JSON</a></p>"
    graph = oeuvreid2graph(record, dict_entities, size="20,20")
    svg_graph = f"graphs/{recordid}.gv.svg"
    # div_graph = f'<a target="blank" href="{svg_graph}" title="Afficher le graphe"><img src = "{svg_graph}" alt="Graphe de l\'oeuvre"/>'
    div_graph = f'\n<div class="graph">{graphfilename2content(svg_graph)}</div>\n'
    infos_pro += div_graph
    indexed_metas = display_indexed_metas(record)
    infos_pro += indexed_metas
    marc_record = record.txt.replace("\n", "<br/>")
    marc_record = f'<p class="marc_record">{marc_record}</p>'
    infos_pro += marc_record
    return f'\n{infos_pro}\n'
    
def graphfilename2content(graphfilename):
    svg_content = etree.parse(os.path.join("results", graphfilename))
    svg_content = svg_content.xpath("//s:svg", namespaces={"s": "http://www.w3.org/2000/svg"})[0]
    svg_content = etree.tostring(svg_content).decode("utf-8")
    return svg_content

def display_indexed_metas(record):
    # Afficher les métadonnées indexées par le moteur de recherche
    indexed_metas = '<div class="indexed_metas">\n<table class="indexed_metas_table">\n'
    indexed_metas += f"<tr><th>self_index</th><td>{record.self_index}</td></tr>\n"
    indexed_metas += f"<tr><th>linked_entities_index</th><td>{record.linked_entities_index}</td></tr>\n"
    indexed_metas += f"<tr><th>resp_index</th><td>{record.resp_index}</td></tr>\n"
    indexed_metas += f"<tr><th>linked_resp_index</th><td>{record.linked_resp_index}</td></tr>\n"
    indexed_metas += f"<tr><th>global_index</th><td>{record.global_index}</td></tr>\n"
    indexed_metas += "</table>\n</div>\n"
    return indexed_metas

def generate_work_filters(record):
    # A partir d'une notice d'oeuvre, générer une liste de liens
    # (<a href=''>) permettant de gérer des filtres
    
    # Première ligne de filtres (moteur de recherche, langues, dates)
    header = "<h3>Filtres</h3>"
    filter_form = "<input type='form' width='150px' value='Limiter les résultats'/>"
    filter_avail = "<a href='#'>Disponible</a>"
    filters_lng = ""
    for lang in record.lang:
        try:
            link = f'<a class="filters_lng" href="#">{dict_lang2label[lang]}</a>'
        except KeyError:
            link = f'<a class="filters_lng" href="#">{lang}</a>'
        filters_lng += f" {link}"
    filters_content_type = []
    if record.type == "o":
        for expr_content_type in record.exprContentType:
            link = f'<a class="filters_content_type" href="#">{expr_content_type}</a>'
            filters_content_type.append(link)
    """else:
        link = f'<a class="filters_content_type" href="#">{record.exprContentType}</a>'
        filters_content_type = [link]"""
    filters_content_type = " ".join(filters_content_type)
    year_range = generate_year_range(record)
    filters_elements = [filter_form, filter_avail, filters_lng, filters_content_type, year_range]
    filters1 = f"<div class='filters1'>{' '.join(filters_elements)}</div>"

    # Deuxième ligne (mentions de responsabilités des expressions)
    links_resp = []
    for resp in record.exprResp:
        link = f'<a href="#">{resp}</a>'
        links_resp.append(link)
    links_resp = " | ".join(links_resp)
    filters2 = f"<div class='filters2'>{links_resp}</div>"
    return "\n".join([header, filters1, filters2])


def generate_year_range(record):
    """
    Génération d'une réglette à double limite pour les années
    """
    doublerange = "<div class='yearRange'><p>Filtre par année</p>"
    """ if record.manifsYears is not None and len(record.manifsYears) > 1:
        # doublerange = '<form>\n<div data-role="rangeslider">\n<label for="range-1a"></label>'
        doublerange += f'<input type="range" name="range-1a" id="range-1a" min="{str(record.manifsYears[0])}" max="{record.manifsYears[-1]}" value="{str(record.manifsYears[0])}" data-popup-enabled="true" data-show-value="true">'
        doublerange += f'<input type="range" name="range-1a" id="range-1a" min="{str(record.manifsYears[0])}" max="{str(record.manifsYears[-1])}" value="{str(record.manifsYears[0])}" data-popup-enabled="true" data-show-value="true">'
        doublerange += '<label for="range-1b"></label>'
        doublerange += f'<input type="range" name="range-1b" id="range-1b" min="{str(record.manifsYears[0])}" max="{str(record.manifsYears[-1])}" value="{str(record.manifsYears[-1])}" data-popup-enabled="true" data-show-value="true">'
        doublerange += "</div>\n</form>"""
    doublerange += "</div>"
    return doublerange

def generate_entete(query, type_entity, no_resultat=0):
    entete = '\n<div class="entete">'
    entete += f'\n<p>Rappel de la recherche : <strong>{query}</strong></p>'
    if no_resultat:
        # En tête d'une notice détaillée
        entete += f"\n<p class='back'><a href='short_results_{type_entity}.html'>Retour à la liste des résultats</a></p>"
        entete += f'<h1>Résultat {str(no_resultat)}</h1>'
    else:
        # En tête d'une liste de résultats
        dict_type_entity = {"e": "versions", "o": "oeuvres"}
        link_alt = {"e": '<p class="alt_list"><a href="short_results_o.html">Regrouper les résultats par oeuvres</a></p>',
                    "o": '<p class="alt_list"><a href="short_results_e.html">Distinguer les résultats par versions</a></p>'}
        entete += f"<h1>Liste des résultats par {dict_type_entity[type_entity]}</h1>"
        entete += link_alt[type_entity]
    entete += "</div>"
    return entete


def write_html_head(file, html_title, type_entity):
    file.write(f"<html>\n<head>\n<meta charset='UTF-8'>\n<title>{html_title}</title>\n\
<link rel='stylesheet' href='../styles.css'/>")
    """file.write('<link rel="stylesheet" href="https://demos.jquerymobile.com/1.4.2/css/themes/default/jquery.mobile-1.4.2.min.css">')
    file.write('<script src="https://demos.jquerymobile.com/1.4.2/js/jquery.js"></script>')
    file.write('<script src="https://demos.jquerymobile.com/1.4.2/js/jquery.mobile-1.4.2.min.js"></script>')"""
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
        if ".html" in filename and "form" not in filename:
            os.remove(f"results/{filename}")
        if ".json" in filename:
            os.remove(f"results/{filename}")
    for filename in os.listdir("results/graphs"):
            os.remove(f"results/graphs/{filename}")
