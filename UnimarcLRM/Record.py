# coding: utf-8

"""

Définition d'une classe d'objet Record
avec 4 (ou +) sous-classes:
 * Item
 * Manif
 * Expression
 * Oeuvre

Les attributs communs sont 
 * l'identifiant : .id
 * le type d'entité : .type
 * la notice en XML et en texte : .xml et .txt
 * un "label" (pas tout à fait un point d'accès en bonne et due forme) : .label
 * les statistiques des zones et sous-zones (dictionnaire) : .stats_zones
 * les liens aux mentions de responsabilités (dictionnaire) : .resp

Chaque entité a en plus un attribut listant (dictionnaire) la ou les entités supérieures auxquelles elle est liée : 
 * items : .toManifs
 * manifs : .toExpressions
 * expressions : .toOeuvres

"""

from collections import defaultdict
from lxml import etree
from string import ascii_lowercase
import re
from string import punctuation
from unidecode import unidecode
from textwrap import wrap

import SRUextraction as sru # import du fichier https://github.com/Lully/bnf-sru/blob/master/SRUextraction.py
from common_dicts import *

dic_id2type = {}
dict_entities = {}

ns = {"marc": "http://www.loc.gov/MARC21/slim"}

class Record:
    def __init__(self, xml_record, rectype):
        self.xml = xml_record
        self.init_type = rectype
        self.id = sru.record2fieldvalue(self.xml, "001")
        self.txt = sru.xml2seq(self.xml)
        self.self_index, self.linked_entities_index, self.resp_index, self.linked_resp_index, self.global_index = [[], [], [], [], []]
        self.type = get_type(xml_record, rectype)
        self.label = get_label(self)
        self.label_html = html_label(self.label)
        self.splitted_label = split_label(self.label, self.type)
        self.stats_zones = get_stats_zones(xml_record)
        self.resp = get_responsabilites(xml_record, self.type)
        self.respIds = get_respids(xml_record, self.type)
        self.toOeuvres = defaultdict(str)
        self.toExpressions = defaultdict(str)
        self.toManifs = defaultdict(str)
        self.manifsYears = None
        self.toItems = defaultdict(str)
        self.other_expressions = dict()

        self = construct_indexation(self, {})
        dic_id2type[self.id] = self.type
        self.repr = f"id : {self.id}\ntype initial : {self.init_type} ; type : {self.type}\n\
label : {self.label}\n\nNotice : {self.txt} \n\nXML : {self.xml}\n\
Indexation : {self.global_index}"
    
    def __repr__(self):
        representation = self.repr
        return representation


class Manifestation(Record):
    def __init__(self, xml_record, rectype):
        super().__init__(xml_record, rectype)
        self.title = manif2title(xml_record)
        self.publisher = manif2publish(xml_record)
        self.description = manif2description(xml_record)
        self.toExpressions = manif2expression(self.xml)

    def __repr__(self):
        representation = self.repr
        representation += f"\nLiens aux autres entités :\n\
Vers Oeuvres : {str(self.toOeuvres)}\n\
Vers expressions : {str(self.toExpressions)}\n\
Vers items : {str(self.toItems)}"
        return representation


def manif2title(xml_record):
    # 200$a : 200$e. 200$f, 200$g
    title = sru.record2fieldvalue(xml_record, "200$a")
    f200e = ", ".join(sru.record2fieldvalue(xml_record, "200$e").split("¤"))
    f200f = ", ".join(sru.record2fieldvalue(xml_record, "200$f").split("¤"))
    f200g = ", ".join(sru.record2fieldvalue(xml_record, "200$g").split("¤"))
    if f200e:
        title += f" : {f200e}"
    if f200f:
        title += f" / {f200f}"
    if f200g:
        title += f", {f200g}"
    return title

def manif2publish(xml_record):
    publisher = ""
    f214a = "-".join(sru.record2fieldvalue(xml_record, "214$a").split("¤"))
    f214c = ", ".join(sru.record2fieldvalue(xml_record, "214$c").split("¤"))
    f214d = ", ".join(sru.record2fieldvalue(xml_record, "214$d").split("¤"))
    publisher = ". ".join([el for el in [f214a, f214c, f214d] if el])
    return publisher

def manif2description(xml_record):
    return ""



class Oeuvre(Record):
    def __init__(self, xml_record, rectype):
        super().__init__(xml_record, rectype)
        self.subjects = get_subjects(xml_record)
        self.genreforme = get_genreforme(xml_record)
        self.detailed = construct_detailed_record(self, ["231", "241"], ["370", "378"], ["640"])
        self.rebonds, self.rebondids = get_rebonds(self, ["531", "541", "515"])
        self.exprResp = None  # Mentions de responsabilités aux niveau des expressions
        self.lang = None
        self.exprContentType = None

    def __repr__(self):
        representation = self.detailed + "\n"*2 + self.repr
        representation += f"\nLiens aux autres entités :\n\
Vers expressions : {str(self.toExpressions)}\n\
Vers manifestations : {str(self.toManifs)}\n\
Vers items : {str(self.toItems)}"
        return representation


def html_label(label):
    html_label = label
    html_label = re.sub(f"[,\.] {re_content_type}[,\.]?", 
                        r" <img src='icons/\1.png' alt='[\1]' title='\1'/>", html_label)
    return html_label


def get_subjects(xml_record):
    subjects = {}
    for tag in tags_subjects["sujet"]:
        for field_occ in xml_record.xpath(f"*[@tag='{tag}']"):
            indexid = sru.field2subfield(field_occ, "3")
            try:
                value = dict_entities[indexid].label
            except KeyError:
                value = ""
            subjects[indexid] = value
    return subjects

def get_genreforme(xml_record):
    gf = {}
    for tag in tags_subjects["genre-forme"]:
        for field_occ in xml_record.xpath(f"*[@tag='{tag}']"):
            indexid = sru.field2subfield(field_occ, "3")
            try:
                value = dict_entities[indexid].label
            except KeyError:
                value = ""
            gf[indexid] = value
    return gf

                
def normalize_date(date):
    reg1 = "#(\d\d\d\d)(\d\d)(\d\d)#"
    reg2 = "#(\d\d\d\d).+#"
    new_date = ""
    if re.fullmatch(reg1, date) is not None:
        new_date = re.sub(reg1, r"\3/\2/\1", date)
    elif re.fullmatch(reg2, date) is not None:
        new_date = re.sub(reg2, r"\1", date)
    return new_date


def split_label(label, entity_type):
    # renvoie un label avec sauts de ligne
    # pour faciliter l'affichage dans le graphe
    if entity_type == "m":
        nb = 10
    else:
        nb = 20
    splitted_label = "\n".join(wrap(label, nb))
    # print(splitted_label)
    return splitted_label

def clean_string(string):
    # renvoie une version nettoyée (sans ponctuation ni majuscules)
    string = string.lower()
    for char in punctuation:
        string = string.replace(char, " ")
    string = " ".join([el for el in string.split(" ") if len(el) > 1])
    string = unidecode(string)
    return string


def construct_indexation(record, dict_entities):
    # construction de l'indexation
    """global_index = record.global_index
    self_index = record.self_index             # Métadonnées dans l'entité même
    linked_entities_index = record.linked_entities_index  # métadonnées des entités OEMI en lien
    resp_index = record.resp_index          # métadonnées pour les mentions de responsabilité
    linked_resp_index = record.linked_resp_index      # métadonnées des mentions de responsabilités en lien
    """ 
    tags = tags_indexation[record.type]
    for tag in tags:
        current_value = sru.record2fieldvalue(record.xml, tag)
        current_value = re.sub(" ?$. ", " ", current_value)
        current_value = clean_string(current_value)
        if current_value:
            record.self_index.append(current_value)
    for dico in [record.toOeuvres, record.toExpressions, record.toManifs, record.toItems]:
        values = []
        if type(dico) == dict:
            for key in dico:
                values.append(clean_string(dico[key]))
        record.linked_entities_index.extend(values)
    for resp_label in record.resp:
        if clean_string(resp_label):
            record.resp_index.append(clean_string(resp_label))
    if dict_entities:
        if record.type == "m":
            for expr in record.toExpressions:
                if expr:
                    expr_rec = dict_entities[expr]
                    for resp_label in expr_rec.resp:
                        if clean_string(resp_label):
                            record.linked_resp_index.append(clean_string(resp_label))
            for oeuvre in record.toOeuvres:
                oeuvre_rec = dict_entities[oeuvre]
                for resp_label in oeuvre_rec.resp:
                    if clean_string(resp_label):
                        record.linked_resp_index.append(clean_string(resp_label))
        elif record.type == "e":
            for manif in record.toManifs:
                manif_rec = dict_entities[manif]
                for resp_label in manif_rec.resp:
                    if clean_string(resp_label):
                        record.linked_resp_index.append(clean_string(resp_label))
                for el in manif_rec.self_index:
                    if el:
                        record.linked_entities_index.append(el)
            for oeuvre in record.toOeuvres:
                oeuvre_rec = dict_entities[oeuvre]
                for resp_label in oeuvre_rec.resp:
                    if clean_string(resp_label):
                        record.linked_resp_index.append(clean_string(resp_label))
                for el in oeuvre_rec.self_index:
                    if el:
                        record.linked_entities_index.append(el)
        elif record.type == "o":
            for manif in record.toManifs:
                manif_rec = dict_entities[manif]
                for resp_label in manif_rec.resp:
                    record.linked_resp_index.append(clean_string(resp_label))
                for el in manif_rec.self_index:
                    record.linked_entities_index.append(el)
            for expr in record.toExpressions:
                if expr:
                    expr_rec = dict_entities[expr]
                    for resp_label in expr_rec.resp:
                        if clean_string(resp_label):
                            record.linked_resp_index.append(clean_string(resp_label))
                    for el in expr_rec.self_index:
                        if el:
                            record.linked_entities_index.append(el)
    record.global_index = record.self_index + record.linked_entities_index + record.resp_index + record.linked_resp_index
    record.global_index = " ".join(set(record.global_index))
    return record


def zones2recorddescription(xml_record, list_tags):
    description = []
    for tag in list_tags:
        for field in xml_record.xpath(f"*[@tag='{tag}']"):
            subf_p = sru.field2subfield(field, "p")
            desc = []
            for subf in "atcf":
                desc.append(sru.field2subfield(field, subf))
            try:
                desc.append(dict_entities[sru.field2subfield(field, "3")].label)
            except KeyError:
                pass
                # print(sru.field2subfield(field, "3"))
            desc = [el for el in desc if el]
            desc = ", ".join(desc)
            if subf_p:
                desc = f"{subf_p} {desc}"
            """print(tag, field, desc)
            print(etree.tostring(field))"""
            description.append(desc)  
    description = ".\n".join([el for el in description if el])
    description = description.replace("¤", ". ")
    return description     


class Expression(Record):
    def __init__(self, xml_record, rectype):
        super().__init__(xml_record, rectype)
        self.lang = get_expression_language(xml_record)
        self.toOeuvres  = expression2oeuvre(self.xml)
        self.expressionContentType = get_expression_content_type(self.xml)
        self.exprContentType = self.expressionContentType
        self.exprResp = get_exprResp(self)
        self.detailed = construct_detailed_record(self, ["232", "242"], ["371"], ["640"])
        self.detailed_sup = None       # Métadonnées venues des entités en lien
        self.rebonds, self.rebondids = get_rebonds(self, ["531", "541", "515"])
        self.other_works_expressions = None


    def __repr__(self):
        representation = self.repr
        representation += f"\nLiens aux autres entités :\n\
Vers Oeuvres : {str(self.toOeuvres)}\n\
Vers manifestations : {str(self.toManifs)}\n\
Vers items : {str(self.toItems)}"
        return representation


def get_exprResp(expression):
    exprResp = []
    for resp in expression.resp:
        for role in expression.resp[resp]:
            exprResp.append(f"{resp} ({role})")
    return exprResp


def get_expression_language(xml_record):
    # Récupérer la langue de l'expression
    languages = [sru.record2fieldvalue(xml_record, "101$a")]
    languages = "¤".join(languages)
    languages = [el for el in languages.split("¤") if el]
    return list(set(languages))
            

def get_expression_content_type(xml_record):
    expression_content_type = ""
    f154a = sru.record2fieldvalue(xml_record, "154$a")        
    if f154a and f154a[1] == "b":
        for f242n in sru.record2fieldvalue(xml_record, "242$n").split("¤"):
            if f242n:
                if expression_content_type == "":
                    expression_content_type = f242n
        if expression_content_type == "":
            for f232c in sru.record2fieldvalue(xml_record, "232$c").split("¤"):
                if f232c:
                    if expression_content_type == "":
                        expression_content_type = f232c
        if expression_content_type == "":
            for f232n in sru.record2fieldvalue(xml_record, "232$n").split("¤"):
                if f232n:
                    if expression_content_type == "":
                        expression_content_type = f232n
        if expression_content_type == "":
            for f542n in sru.record2fieldvalue(xml_record, "542$n").split("¤"):
                if expression_content_type == "":
                    expression_content_type = f542n
    return expression_content_type


def construct_detailed_record(record, accesspoint_tag, description_tags, 
                              others_infos_tags):
    """Notice détaillée d'oeuvre :
231$a. 231$c (231$d) - 231$m
Description : 531$p + label(531$3). 541 $p + label(541$3)
Autres infos : 640$0 : [640$f à normaliser] (640$d)"""
    row = []
    first_line = []

    for tag in accesspoint_tag:
        for field_occ in record.xml.xpath(f"*[@tag='{tag}']"):
            for subf in field_occ.xpath("*"):
                code = subf.get("code")
                if code in ascii_lowercase.replace("o", ""):
                    first_line.append(subf.text.replace("¤", ", "))
    first_line = ". ".join(first_line)
    # row.append(first_line)
    description = zones2recorddescription(record.xml, description_tags)
    if description:
        row.append(f"Description : {description}")
    autres_infos = []
    for tag in others_infos_tags:
        for field_occ in record.xml.xpath(f"*[@tag='{tag}']"):
            val = sru.field2subfield(field_occ, "0")
            if sru.field2subfield(field_occ, "f"):
                val += f" : {normalize_date(sru.field2subfield(field_occ, 'f'))}"
            if sru.field2subfield(field_occ, "d"):
                val += f" ({sru.field2subfield(field_occ, 'd')})"
            autres_infos.append(val)
    autres_infos = "\n".join(autres_infos)
    row.append("\n")
    row.append(autres_infos)
    if sru.field2subfield(record.xml, "370$c"):
        row.append(sru.field2subfield(record.xml, "370$c"))

    row = "\n".join(row)
    return row



class Item(Record):
    def __init__(self, xml_record, rectype):
        super().__init__(xml_record, rectype)
        self.toManifs  = item2manif(self.xml)
        self.localisation, self.cote = get_cote(xml_record)
    
    def __repr__(self):
        representation = self.repr
        representation += f"\n\nManif en lien : {self.toManifs}"
        return representation
        
def get_cote(xml_record):
    # récupérarion de la localisation et de la cote
    # d'un item
    localisation = sru.record2fieldvalue(xml_record, "801$b")
    cote = " ".join([sru.record2fieldvalue(xml_record, "252$b"), sru.record2fieldvalue(xml_record, "252$j")])
    return localisation, cote


def get_rebonds(record, rebonds_tags):
    rebonds = []
    rebondids = []
    for tag in rebonds_tags:
        for field_occ in record.xml.xpath(f"*[@tag='{tag}']"):
            oid = sru.field2subfield(field_occ, '3').split("¤")[0]
            if oid:
                rebondids.append(oid)
                link = f"full_results_{oid}.html"
                text = []
                for subf in field_occ.xpath("*"):
                    code = subf.get("code")
                    if code in ascii_lowercase:
                        text.append(subf.text)
                text = " ".join(text)
                text = html_label(text)
                if link:
                    rebonds.append(f"<span class='rebond'><a href='{link}'>{text}</a></span>")
                else:
                    rebonds.append(f"<span class='rebond'>{text}</span>")
    rebonds = "\n".join(rebonds)
    return rebonds, rebondids

def get_stats_zones(xml_record):
    # Renvoie un dictionnaire listant les zones avec leur nombre d'occurrences
    stats_zones = defaultdict(int)
    for field in xml_record.xpath("*[@tag]"):
        stats_zones[field.get("tag")] += 1
    for field in xml_record.xpath("*[local-name()!='leader']"):
        if field.get("tag") is None :
            stats_zones[""] += 1
    for field in xml_record.xpath("m:datafield[@tag]", namespaces={"m":"http://www.loc.gov/MARC21/slim"}):
        if field.get("ind1") is None:
            stats_zones[f'{field.get("tag")} ind1 vide'] += 1
        if field.get("ind2") is None:
            stats_zones[f'{field.get("tag")} ind2 vide'] += 1
    return stats_zones


def item2manif(xml_record):
    dict_manifs = {}
    for f004 in xml_record.xpath(f"*[@tag='004']"):
        recordid = f004.text
        label = "Exemplaire " + xml_record.find(f"*[@tag='001']").text
        dict_manifs[recordid] = None
    return dict_manifs


def manif2expression(xml_record):
    dict_expressions = {}
    for tag in tags_manif2expressions:
        for field_occ in xml_record.xpath(f"*[@tag='{tag}']"):
            recordid = sru.field2subfield(field_occ, "3")
            accesspoint = accesspoint2label(field_occ)
            dict_expressions[recordid] = accesspoint
    return dict_expressions

def expression2oeuvre(xml_record):
    dict_oeuvres = {}
    for tag in tags_expression2oeuvres:
        for field_occ in xml_record.xpath(f"*[@tag='{tag}']"):
            recordid = sru.field2subfield(field_occ, "3")
            accesspoint = accesspoint2label(field_occ)
            if sru.field2subfield(field_occ, "p"):
                accesspoint = f"({sru.field2subfield(field_occ, 'p')}) {accesspoint}"
            dict_oeuvres[recordid] = accesspoint
    return dict_oeuvres


    
def accesspoint2label(field):
    # Construction du point d'accès sans $
    label = []
    for subf in field.xpath("*[@code]"):
        code = subf.get("code")
        if code in ascii_lowercase.replace("p", "") and subf.text:
            label.append(subf.text)
    label = ", ".join(label)
    return label
    
def get_type(xml_record, rectype):
    entity_type = None
    if rectype in "mi":
        entity_type = rectype
    elif rectype in "oe":
        equiv = {"a": "o", "b": "e", "x": "x"}
        f154a = sru.record2fieldvalue(xml_record, "154$a")
        if f154a and f154a[1] in equiv:
            entity_type = equiv[f154a[1]]
        else:
            entity_type = "z"
            print(etree.tostring(xml_record))
            raise
    elif rectype == "p":
        # Fichier Autres entités
        # p : personne, c : collectivité, l : label (marque)
        # t : laps de temps, g : genre-forme
        label_field = ""
        tag2type = {"200": "p", "210": "c", "216": "l",
                    "215": "n", "250": "t", "280": "g"}
        for field in xml_record.xpath("*[@tag]"):
            try:
                if field.get("tag")[0] == "2":
                    label_field = field.get("tag")
            except TypeError:
                print(etree.tostring(xml_record))
                raise
        entity_type = tag2type[label_field]
    if entity_type is None:
        print(etree.tostring(xml_record))
    return entity_type
            
        
def get_label(record):
    label = []
    if record.type in "mipclgt":
        label.append(sru.record2fieldvalue(record.xml, "200$a"))
        label.append(sru.record2fieldvalue(record.xml, "200$f"))
        label.append(sru.record2fieldvalue(record.xml, "252$a"))
        label.append(sru.record2fieldvalue(record.xml, "252$b"))
        label.append(sru.record2fieldvalue(record.xml, "252$j"))
        label.append(sru.record2fieldvalue(record.xml, "214$c"))
        label.append(sru.record2fieldvalue(record.xml, "214$d"))
        label.append(sru.record2fieldvalue(record.xml, "210$a"))
        label.append(sru.record2fieldvalue(record.xml, "210$b"))
        label.append(sru.record2fieldvalue(record.xml, "210$c"))
        label.append(sru.record2fieldvalue(record.xml, "250$a"))
        label.append(sru.record2fieldvalue(record.xml, "250$x"))
        label.append(sru.record2fieldvalue(record.xml, "215$a"))
        label.append(sru.record2fieldvalue(record.xml, "215$b"))
        label.append(sru.record2fieldvalue(record.xml, "215$c"))
        label.append(sru.record2fieldvalue(record.xml, "216$a"))
        label.append(sru.record2fieldvalue(record.xml, "216$b"))
        label.append(sru.record2fieldvalue(record.xml, "216$c"))
        label.append(sru.record2fieldvalue(record.xml, "280$a"))
    elif record.type in "eox":
        for field in record.xml.xpath("*[@tag]"):
            tag = field.get("tag")
            if tag.startswith("2"):
                if sru.field2subfield(field, "a"):
                    label.append(sru.field2subfield(field, "a"))
                if record.type in "oe":
                    label.append(sru.field2subfield(field, "c"))
                if record.type in "oe":
                    label.append(sru.field2subfield(field, "d"))
                if record.type in "oe":
                    label.append(sru.field2subfield(field, "t"))
                if record.type in "oe":
                    label.append(sru.field2subfield(field, "m"))
                if record.type in "oe":
                    label.append(sru.field2subfield(field, "w"))
                if record.type in "oe":
                    label.append(sru.field2subfield(field, "n"))
                else:
                    label.append("*"*20)
                    label.append("$a vide")
                    label.append(sru.field2value(field))
    if record.type in "i":
        label = " > ".join([el for el in label if el.strip()])
    else:
        label = ", ".join([el for el in label if el.strip()])
    label = label.replace("¤", " - ")
    return label


def get_responsabilites(xml_record, rectype):
    resp = {}
    if rectype in tags_resp:
        for tag in tags_resp[rectype]:
            for field_occ in xml_record.xpath(f"*[@tag='{tag}']"):
                label_entity = []
                roles = []
                for subf in "abc":
                    for subf_occ in field_occ.xpath(f"*[@code='{subf}']"):
                        label_entity.append(subf_occ.text)
                try:
                    for subf4 in field_occ.xpath("*[@code='4']"):
                        roles.append(ROLES[subf4.text])
                except KeyError:
                    print(rectype, f'"{sru.record2fieldvalue(xml_record, "001")}"', f"'{subf4.text}'")
                label_entity = ", ".join(label_entity)
                resp[label_entity] = roles
    return resp

def get_respids(xml_record, rectype):
    respids = set()
    if rectype in tags_resp:
        for tag in tags_resp[rectype]:
            for field_occ in xml_record.xpath(f"*[@tag='{tag}']"):
                respids.add(sru.field2subfield(field_occ, "3"))
    return respids