# coding: utf-8

explain = """Exécution sous forme de script Python des différentes
étapes documentées dans le notebook, afin de raccourcir celui-ci 
dans une version qui met en avant l'affichage des résultats
"""

from Record import *
from common_dicts import * 

def generate_dict_entities(oeuvres_expressions_filename, 
                           manifs_filename,
                           items_filename,
                           autres_entites_filename):
    # génère un dictionnaire des entités
    dict_entities = dict()
    manifs_file = etree.parse(manifs_filename)
    oeuvres_expressions_file = etree.parse(oeuvres_expressions_filename)
    items_file = etree.parse(items_filename)
    autres_entites_file = etree.parse(autres_entites_filename)

    manifs = [Manifestation(manif, "m") for manif in manifs_file.xpath(".//marc:record", namespaces=ns)]
    oeuvres_expr = [Record(oe, "oe") for oe in oeuvres_expressions_file.xpath(".//marc:record", namespaces=ns)] 
    items = [Item(oe, "i") for oe in items_file.xpath(".//marc:record", namespaces=ns)] 
    autres_entites = [Record(r, "p") for r in autres_entites_file.xpath(".//marc:record", namespaces=ns)] 

    oeuvres = []
    expressions = []
    oeuvres_or_expressions = []
    for entity in oeuvres_expr:
        if entity.type == "o":
            oeuvre = Oeuvre(entity.xml, entity.init_type)
            oeuvres.append(oeuvre)
            
        elif entity.type == "e":
            expression = Expression(entity.xml, entity.init_type)
            expressions.append(expression)
        else:
            oeuvres_or_expressions.append(entity)
    for entity in items + manifs + expressions + oeuvres + autres_entites:
        dict_entities[entity.id] = entity
    dict_entities = add_suppl_links(dict_entities, oeuvres, expressions, manifs, items)
    dict_entities = enrich_oeuvres(dict_entities)
    return dict_entities


def add_suppl_links(dict_entities, oeuvres, expressions, manifs, items):
    # Après une première initialisation de dict_entities
    # on enrichit chaque entité du contenu des autres
    dict_manif2item = defaultdict(list)
    for item in items:
        for manif in item.toManifs:
            try:
                manif_accesspoint = dict_entities[manif].label
            except KeyError:
                print("Manifestation", manif, f"mentionnée dans l'item {item.id} mais absente du fichier des manifestations")
            item.toManifs[manif] = manif_accesspoint
            dict_manif2item[manif].append(item.id)
    for expr in expressions:
        for oeuvre in expr.toOeuvres:
            dict_entities[oeuvre].toExpressions[expr.id] = expr.label
    for manif in manifs:
        for expr in manif.toExpressions:
            if expr:
                for oeuvre in dict_entities[expr].toOeuvres:
                    dict_entities[oeuvre].toManifs[manif.id] = manif.label
    for item in items:
        for manif in item.toManifs:
            for expr in dict_entities[manif].toExpressions:
                if expr:
                    for oeuvre in dict_entities[expr].toOeuvres:
                        dict_entities[oeuvre].toItems[item.id] = item.label
    # régénération de la liste des oeuvres
    oeuvres = [dict_entities[o] for o in dict_entities if dict_entities[o].type == "o"]        
    for manif in manifs:
        for expr in manif.toExpressions:
            if expr:
                dict_entities[expr].toManifs[manif.id] = manif.label
    for expr in dict_entities:
        if dict_entities[expr].type == "e":
            for manif in dict_entities[expr].toManifs:
                items_list = dict_manif2item[manif]
                for item in items_list:
                    dict_entities[expr].toItems[item] = dict_entities[item].label
    # régénération de la liste des expressions
    expressions = [dict_entities[e] for e in dict_entities if dict_entities[e].type == "e"]
    for manif in manifs:
        for expr in manif.toExpressions:
            if expr:
                oeuvres_list = dict_entities[expr].toOeuvres
                for oeuvre in oeuvres_list:
                    dict_entities[manif.id].toOeuvres[oeuvre] = dict_entities[oeuvre].label
        for item in dict_manif2item[manif.id]:
            dict_entities[manif.id].toItems[item] = dict_entities[item].label
    # régénération de la liste des expressions
    manifs = [dict_entities[m] for m in dict_entities if dict_entities[m].type == "m"]
    for item in items:
        for manif in item.toManifs:
            manif_entity = dict_entities[manif]
            for expr in manif_entity.toExpressions:
                if expr:
                    dict_entities[item.id].toExpressions[expr] = dict_entities[expr].label
            for oeuvre in manif_entity.toOeuvres:
                dict_entities[item.id].toOeuvres[oeuvre] = dict_entities[oeuvre].label
    return dict_entities


def enrich_oeuvres(dict_entities):
    # Enrichissement des métadonnées des oeuvres
    for e in dict_entities:
        if dict_entities[e].type == "o":
            dict_entities[e].lang = expr_lang2oeuvre(e, dict_entities[e], dict_entities)
    return dict_entities


def expr_lang2oeuvre(oid, o_entity, dict_entities):
    # renvoi d'un set de langues à partir de la langue des expressions
    lang = set()
    for expr in o_entity.toExpressions:
        language = [sru.record2fieldvalue(dict_entities[expr].xml, "101$a"), sru.record2fieldvalue(dict_entities[expr].xml, "101$c")]
        language = "¤".join(language)
        language = [el for el in language.split("¤") if el]
        for l in language:
            lang.add(l)
    return lang

if __name__ == "__main__":
    list_files = ["UMA_Oeuvres_Expressions.xml",
                  "UMB_Manifestations.xml",
                  "UMH_Items.xml",
                  "UMA_Autres_Entites_Liees.xml"]
    dict_entities = generate_dict_entities(list_files)