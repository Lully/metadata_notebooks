# coding: utf-8

import os

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
    i = 0
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
    file.write("\n</body>\n")

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
