# coding: utf-8

ROLES = {"000": "Fonction à préciser", "003": "Encadrant académique", "005": "Acteur", "010": "Adaptateur", "015": "Agence mettant à disposition la reproduction", "018": "Auteur de l'animation", "020": "Annotateur", "030": "Arrangeur", "040": "Artiste", "050": "Autre détenteur du privilège", "060": "Nom associé à l'exemplaire", "062": "Auteur présumé", "065": "Commissaire-priseur", "070": "Auteur", "072": "Auteur des citations ou des fragments textuels", "075": "Auteur de la postface, du colophon, etc.", "080": "Préfacier, etc.", "090": "Dialoguiste", "100": "Auteur d'oeuvre adaptée ou continuée", "110": "Relieur", "120": "Maquettiste de la reliure", "130": "Maquettiste", "140": "Concepteur de la jaquette", "150": "Concepteur de l'ex-libris", "160": "Libraire", "170": "Calligraphe", "180": "Cartographe", "190": "Censeur", "195": "Chef de choeur", "200": "Chorégraphe", "202": "Artiste de cirque", "205": "Collaborateur", "206": "Collecteur", "207": "Humoriste", "210": "Commentateur", "212": "Auteur du commentaire", "220": "Compilateur", "230": "Compositeur", "233": "Compositeur de l'oeuvre adaptée", "236": "Compositeur de l'oeuvre principale", "240": "Compositeur d'imprimerie", "245": "Concepteur de l'idée originale", "250": "Chef d'orchestre", "255": "Consultant de projet", "257": "Auteur (continuateur)", "260": "Détenteur du copyright", "270": "Correcteur (manuscrits)", "273": "Commissaire d'exposition", "275": "Danseur", "280": "Dédicataire", "290": "Dédicateur", "295": "Organisme de soutenance", "300": "Metteur en scène ou réalisateur", "303": "Disc jockey", "305": "Candidat", "310": "Distributeur", "320": "Donateur", "330": "Auteur prétendu", "340": "Éditeur scientifique", "350": "Graveur", "355": "Épitomateur", "360": "Aquafortiste", "365": "Expert", "370": "Monteur", "380": "Faussaire", "385": "Ancien auteur présumé ", "390": "Ancien possesseur", "395": "Fondateur", "400": "Bailleur de fonds", "405": "Concepteur de jeu", "407": "Glossateur", "410": "Technicien graphique", "420": "Personne honorée", "430": "Enlumineur", "440": "Illustrateur", "445": "Impresario", "450": "Auteur de l'envoi", "460": "Personne interviewée", "470": "Intervieweur", "475": "Collectivité éditrice", "480": "Librettiste", "490": "Détenteur de licence", "500": "Concédant de licence", "510": "Lithographe", "520": "Parolier", "530": "Graveur sur métal", "535": "Mime", "540": "Moniteur", "545": "Musicien", "550": "Narrateur", "552": "Notaire", "555": "Membre du jury", "557": "Organisateur de réunion", "560": "Instigateur", "570": "Autre", "580": "Fabricant du papier", "582": "Demandeur de brevet", "584": "Inventeur de brevet", "587": "Titulaire de brevet", "590": "Interprète", "595": "Directeur de la recherche", "600": "Photographe", "605": "Présentateur", "610": "Imprimeur", "620": "Imprimeur de gravures", "630": "Producteur", "632": "Directeur artistique", "633": "Membre de l'équipe de production", "635": "Programmeur", "637": "Gestionnaire de projet", "640": "Correcteur sur épreuves", "650": "Éditeur commercial", "651": "Directeur de publication", "655": "Marionnettiste", "660": "Destinataire de lettres", "665": "Producteur de phonogramme", "670": "Ingénieur du son", "672": "Remixeur", "673": "Responsable de l'équipe de recherche", "675": "Responsable du compte-rendu critique", "677": "Membre de l'équipe de recherche", "678": "Restaurateur", "680": "Rubricateur", "690": "Scénariste", "695": "Conseiller scientifique", "700": "Copiste", "705": "Sculpteur", "710": "Secrétaire", "720": "Signataire", "721": "Chanteur", "723": "Mécène", "725": "Organisme de normalisation", "726": "Cascadeur", "727": "Directeur de thèse", "730": "Traducteur", "735": "Translittérateur", "740": "Concepteur de caractères", "750": "Typographe", "753": "Vendeur", "755": "Exécutant vocal", "760": "Graveur sur bois", "770": "Auteur du matériel d'accompagnement", "920": "Propriétaire actuel", "956": "Président du jury de soutenance", "958": "Rapporteur de la thèse", "981": "Laboratoire associé à la thèse", "982": "Entreprise associée à la thèse", "983": "Fondation associée à la thèse", "984": "Equipe de recherche associée à la thèse", "985": "Autre partenaire associé à la thèse", "995": "Organisme de cotutelle", "996": "Ecole doctorale associée à la thèse", "vre": "Voix parlée", "ost": "Ensemble de cordes"}

ENTITY_TYPE = {"i": "item", "m": "manifestation", "e": "expression", "o": "oeuvre"}

tags_manif2expressions = {"507": "point d'accès autorisé Titre (manifestation pointant vers expression)", 
                          "577": "point d'accès autorisé Auteur-Titre (manifestation pointant vers expression)"}

tags_expression2oeuvres = {"232": "point d'accès autorisé Titre",
                           "242": "point d'acècs autorité Auteur-Titre" }

tags_oe2expression = {"532": "Point d’accès autorisé – Titre (expression pointant vers oeuvre)",
                      "542": "Point d’accès autorisé – Auteur/titre (expression pointant vers oeuvre)"}

tags_oe2oeuvre = {"531": "Point d’accès autorisé – Titre (expression pointant vers oeuvre)",
                  "541": "Point d’accès autorisé – Auteur/titre (expression pointant vers oeuvre)",}
# Zones utilisées pour faire des liens aux Personnes et collectivités (avec indicateurs de relations autre que sujet)
tags_resp = {"o": {"501": "Lien aux mentions de responsabilité Personne depuis des oeuvres",
                   "511": "Lien aux mentions de responsabilité Collectivité depuis des oeuvres"},
             "e": {"502": "Lien aux mentions de responsabilité Personne depuis des expressions",
                   "512": "Lien aux mentions de responsabilité Collectivité depuis des expressions"},
             "m": {"702": "Lien de manifestation à une mention de responsabilité Personne",
                   "712": "Lien de manifestation à une mention de responsabilité Collectivité"}}

# Pour chaque type d'entité, les zones à indexer
tags_indexation = {"m": "200,214$a$c$d,225$a$c,307$a,320$a,327$a,330$a".split(","),
                   "e": "232$a,371$a".split(","),
                   "o": "033$a,052$a,231$a,370$a$c,378$a".split(","),
                   "i": "252$a$b$j".split(","),
                   "p": []
                   }
