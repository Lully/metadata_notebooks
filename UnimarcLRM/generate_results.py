# coding: utf-8

import os

def display_html_results(dict_results, dict_entities):
    # A partir d'un lot de notices d'oeuvres comme résultats d'une recherche
    # cette fonction génère 
    #       une page "results/short_results.html"  avec la liste des résultats (abrégés)
    #       et une page "results/full_results_0.html" qui pour chaque résultat génère une page HTML numérotée 
    short_html = generate_short_results_html(dict_results, dict_entities) # renvoie le code HTML
    full_html = generate_full_results_html(dict_results, dict_entities)   # renvoie une liste de code HTML


def generate_short_results_html(dict_results, dict_entities):
    file = open("results/short_results.html", "w", encoding="utf-8")
    write_html_head(file, "Liste de résultats")
    write_html_short_body(file, dict_results)
    write_html_footer(file)

def generate_full_results_html(dict_results, dict_entities):
    i = 0
    for result in dict_results:
        file = open(f"results/full_results_{str(i)}.html", "w", encoding="utf-8")
        write_html_head(file, f"Notice détaillée {result}")
        write_html_full_body(file, result, dict_results[result], dict_entities)
        write_html_footer(file)
        i += 1

def write_html_short_body(file, dict_results):
    file.write("<body>")
    i = 0
    for r in dict_results:
        file.write(f"<p>{str(i)}. <a href='full_results_{str(i)}.html'>{dict_results[r].label}</a></p>")
        i += 1
    file.write("</body>")

def write_html_full_body(file, recordid, record, dict_entities):
    file.write("<body>")
    file.write(f"<p>{record.detailed}</p>")
    file.write("</body>")


def write_html_head(file, html_title):
    file.write(f"<html>\n<head>\n<meta charset='UTF-8'>\n<title>{html_title}</title>\n</head>")


def write_html_footer(file):
    file.write("</html>")
        
def delete_html_results():
    for filename in os.listdir("results"):
        os.remove(f"results/{filename}")
