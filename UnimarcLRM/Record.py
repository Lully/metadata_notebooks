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

import SRUextraction as sru # import du fichier https://github.com/Lully/bnf-sru/blob/master/SRUextraction.py
from common_dicts import *

dic_id2type = {}
dict_entities = {}

class Record:
    def __init__(self, xml_record, rectype):
        self.xml = xml_record
        self.init_type = rectype
        self.id = sru.record2fieldvalue(self.xml, "001")
        self.txt = sru.xml2seq(self.xml)
        self.type = get_type(xml_record, rectype)
        self.label = get_label(self)
        self.stats_zones = get_stats_zones(xml_record)
        self.resp = get_responsabilites(xml_record, self.type)
        self.respIds = get_respids(xml_record, self.type)
        self.toOeuvres = defaultdict(str)
        self.toExpressions = defaultdict(str)
        self.toManifs = defaultdict(str)
        self.toItems = defaultdict(str)
        dic_id2type[self.id] = self.type
        self.repr = f"id : {self.id}\ntype initial : {self.init_type} ; type : {self.type}\n\
label : {self.label}\n\nNotice : {self.txt} \n\nXML : {self.xml}\n"
    
    def __repr__(self):
        representation = self.repr
        return representation


class Manifestation(Record):
    def __init__(self, xml_record, rectype):
        super().__init__(xml_record, rectype)
        self.toExpressions = manif2expression(self.xml)

    def __repr__(self):
        representation = self.repr
        return representation

class Oeuvre(Record):
    def __init__(self, xml_record, rectype):
        super().__init__(xml_record, rectype)
        self.detailed = construct_detailed_work(self)

    def __repr__(self):
        representation = self.repr
        representation += f"Liens aux autres entités :\n\
Vers expressions : {str(self.toExpressions)}\n\
Vers manifestations : {str(self.toManifs)}\n\
Vers items : {str(self.toItems)}"
        return representation


def construct_detailed_work(oeuvre):
    """Notice détaillée d'oeuvre :
231$a. 231$c (231$d) - 231$m
Description : 531$p + label(531$3). 541 $p + label(541$3)
Autres infos : 640$0 : [640$f à normaliser] (640$d)"""
    row = []
    first_line = sru.record2fieldvalue(oeuvre.xml, "231$a")
    if sru.record2fieldvalue(oeuvre.xml, "231$c"):
        first_line += f". {sru.record2fieldvalue(oeuvre.xml, '231$c')}"
    if sru.record2fieldvalue(oeuvre.xml, "231$d"):
        first_line += f" ({sru.record2fieldvalue(oeuvre.xml, '231$d')})"
    if sru.record2fieldvalue(oeuvre.xml, "231$m"):
        first_line += f" - ({sru.record2fieldvalue(oeuvre.xml, '231$m')}"
    row.append(first_line)
    description = zones2recorddescription(oeuvre.xml, ["531", "541"])
    if description:
        row.append(f"Description : {description}")
    autres_infos = []
    for f640 in oeuvre.xml.xpath("*[@tag='640']"):
        val = sru.field2subfield(f640, "0")
        if sru.field2subfield(f640, "d"):
            val += f" : {normalize_date(sru.field2subfield(f640, 'd'))}"
        if sru.field2subfield(f640, "f"):
            val += f" ({sru.field2subfield(f640, 'f')})"
        autres_infos.append(val)
    autres_infos = ". ".join(autres_infos)
    row.append(autres_infos)
    row = "\n".join(row)
    return row
                
def normalize_date(date):
    reg = "#(\d\d\d\d)(\d\d)(\d\d)#"
    new_date = ""
    if re.fullmatch(reg, date) is not None:
        new_date = re.sub(reg, r"$3/$2/$1", date)
    return new_date


def zones2recorddescription(xml_record, list_tags):
    description = []
    for tag in list_tags:
        for field in xml_record.xpath(f"*[@tag='{tag}']"):
            desc = []
            if sru.field2subfield(field, "$p"):
                desc.append(sru.field2subfield(field, "$p"))
            if sru.field2subfield(field, "$3"):
                try:
                    desc.append(dict_entities[sru.field2subfield(field, "$3")].label)
                except KeyError:
                    print(sru.field2subfield(field, "$3"))
            desc = " ".join(desc)
            description.append(desc)  
    description = ". ".join([el for el in description if el])
    return description     


class Expression(Record):
    def __init__(self, xml_record, rectype):
        super().__init__(xml_record, rectype)
        self.toOeuvres  = expression2oeuvre(self.xml)

    def __repr__(self):
        representation += f"Liens aux autres entités :\n\
Vers Oeuvres : {str(self.toOeuvres)}\n\
Vers manifestations : {str(self.toManifs)}\n\
Vers items : {str(self.toItems)}"
        return representation

class Item(Record):
    def __init__(self, xml_record, rectype):
        super().__init__(xml_record, rectype)
        self.toManifs  = item2manif(self.xml)
    
    def __repr__(self):
        representation = self.repr
        representation += f"\n\nManif en lien : {self.toManifs}"
        return representation
        
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
    else:
        entity_type = rectype
    if entity_type is None:
        print(etree.tostring(xml_record))
    return entity_type
            
        
def get_label(record):
    label = []
    if record.type in "mipc":
        label.append(sru.record2fieldvalue(record.xml, "200$a"))
        label.append(sru.record2fieldvalue(record.xml, "200$f"))
        label.append(sru.record2fieldvalue(record.xml, "252$a"))
        label.append(sru.record2fieldvalue(record.xml, "252$b"))
        label.append(sru.record2fieldvalue(record.xml, "252$j"))
    elif record.type in "eox":
        for field in record.xml.xpath("*[@tag]"):
            tag = field.get("tag")
            if tag.startswith("2"):
                if sru.field2subfield(field, "a"):
                    label.append(sru.field2subfield(field, "a"))
                if record.type in "oe":
                    label.append(sru.field2subfield(field, "t"))
                else:
                    label.append("*"*20)
                    label.append("$a vide")
                    label.append(sru.field2value(field))
    if record.type in "i":
        label = " > ".join([el for el in label if el.strip()])
    else:
        label = ", ".join([el for el in label if el.strip()])
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