import pandas as pd
import SRUextraction as sru
from stdf import *
from lxml import etree

corpus = {"Livres": "Books"}
metas = ["ARK", "title", "subject", "description", "source", "language", "relation", "coverage", "creator", "contributor", "publisher", "rights", "date", "type", "format", "identifier"]
report = create_file(f"BibNatFra - Livres.txt", metas)
query = f"bib.frenchNationalBibliography any {corpus['Livres']}"
results = sru.SRU_result(query, parametres={"recordSchema": "dublincore", "maximumRecords": "500"})
"""
for record in results.dict_records:
    xml_record = results.dict_records[record]
    print(etree.tostring(xml_record))"""



for record in results.dict_records:
    xml_record = results.dict_records[record]
    row = [record]
    for meta_name in metas:
        info = xml_record.xpath(f".//*[local-name()='{meta_name}']", namespaces={"dc": "http://purl.org/dc/elements/1.1/", "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/"})
        info = [el.text for el in info]
        info = " ; ".join(info)
        row.append(info)
    line2report(row, report, display=False)
	
"""df = pd.read_csv(report.name, encoding="utf-8", delimiter="\t")
df.to_excel(report.name.replace(".txt", ".xlsx"))"""