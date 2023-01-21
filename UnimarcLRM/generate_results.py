# coding: utf-8

import os
from unidecode import unidecode
from common_dicts import *


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
        file = open(f"results/full_results_{str(i)}.html", "w", encoding="utf-8")
        write_html_head(file, f"Notice détaillée {result}")
        write_html_full_body(file, result, dict_results[result], query, i, dict_entities)
        write_html_footer(file)
        i += 1


def write_html_short_body(file, dict_results, query):
    file.write("<body>")
    file.write(generate_entete(query))

    i = 1
    for r in dict_results:
        file.write(f"<p>{str(i)}. <a href='full_results_{str(i)}.html'>{dict_results[r].label}</a></p>")
        i += 1
    file.write("</body>")

def write_html_full_body(file, recordid, record, query, i, dict_entities):
    # Génération d'une page de notice détaillée
    file.write("\n<body>\n")
    file.write(generate_entete(query, i))
    file.write(f"\n<p>{record.detailed}</p>")
    file.write(f"\n<p class='recordid'>{recordid}</p>")
    filters = generate_work_filters(record)
    file.write(f"\n<p class='filters'>{filters}</p>")
    file.write("\n</body>\n")


def generate_work_filters(record):
    # A partir d'une notice d'oeuvre, générer une liste de liens
    # (<a href=''>) permettant de gérer des filtres
    filter_form = "<input type='form' width='150px' value='Limiter les résultats'/>"
    filters_lng = ""
    for lang in record.lang:
        try:
            link = f'<a class="filters_lng" href="#">{dict_lang2label[lang]}</a>'
        except KeyError:
            link = f'<a class="filters_lng" href="#">{lang}</a>'
        filters_lng += f" {link}"
    filters_elements = [filter_form, filters_lng]
    return " ".join(filters_elements)


def generate_entete(query, no_resultat=0):
    entete = '\n<div class="entete">'
    entete += f'\n<p>Rappel de la recherche : <strong>{query}</strong></p>'
    if no_resultat:
        entete += "\n<p class='back'><a href='short_results.html'>Retour à la liste des résultats</a></p>"
        entete += f'<h1>Résultat {str(no_resultat)}</h1>'
    else:
        entete += "<h1>Liste des résultats</h1>"
    entete += "<div>"
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
        os.remove(f"results/{filename}")
