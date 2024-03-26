#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import re
import xml.etree.ElementTree as ET
import feedparser
from typing import List
import os
from datastructures import Item


def with_re(chemin:str) -> List[Item]:
    nom_fichier = os.path.basename(chemin)
    
    # Lecture du contenu du fichier XML
    with open(chemin, "r") as f:
        contenu = f.read()

    # Expressions régulières pour extraire les balises <item>
    item_pattern = r"<item>(.*?)</item>"
    
    # Recherche des correspondances dans le contenu
    items = re.finditer(item_pattern, contenu, re.DOTALL)
    donnees = []

    # Itération sur les correspondances des balises <item>
    for item in items:
        titre_match = re.search(r"<title>(.*?)</title>", item.group(1), re.DOTALL)
        description_match = re.search(r"<description>(.*?)</description>", item.group(1), re.DOTALL)
        #categorie_match = re.findall(r"<category>(.*?)</category>", item.group(1), re.DOTALL)
        categorie_match = re.finditer("<category\\s?.*?>(.+?)</category>", item.group(1)) # ligne de correction , ajout plusieurs categories
        pubdate_match = re.search(r"<pubDate>(.*?)</pubDate>", item.group(1), re.DOTALL)
        
        # création du dictionnaire d'item
        dictionnaire=Item(
            source="", 
            title="", 
            description="", 
            category=[], 
            pubDate=""
            )
        dictionnaire.source = nom_fichier
        if titre_match:
            titre = titre_match.group(1).strip()
            dictionnaire.title = titre
        if description_match:
            description = description_match.group(1).strip()
            dictionnaire.description = description
        if categorie_match: 
            #categorie = categorie_match
            #dictionnaire["category"] = categorie 
            for category in categorie_match: #  ligne de correction, ajout plusieurs catégories
                dictionnaire.category.append(category.group(1)) #  ligne de correction, ajout plusieurs catégories
        if pubdate_match:
            pubdate = pubdate_match.group(1).strip()
            dictionnaire.pubDate = pubdate
      #  print(categorie)
            #print(dictionnaire)
            donnees.append(dictionnaire)
    
    # renvoie la liste de dico d'items
    return donnees



def with_et(chemin):
    try:
        tree = ET.parse(chemin)
    except ET.ParseError:
        return []
    
    # récpération du nom du fichier
    nom_fichier = os.path.basename(chemin)
    
    # lecture de l'arborescence du fichier xml
    root = tree.getroot()
    id_items = root.findall(".//item")
    
    # création de la liste des items
    liste_totale = []
    title, description, pubDate = None, None, None
    for element in id_items:
        category = []
        if element.find("title") is not None:
            title = element.find("title").text
        if element.find("description") is not None:
            description = element.find("description").text
        if element.find("pubDate") is not None:
            pubDate = element.find("pubDate").text
        if element.find("category") is not None:
            for nb_category in element.findall("category"):
                category_split = nb_category.text.split(",")
                for element in category_split:
                    category.append(element)
        dictionnaire = Item(
            source = nom_fichier,
            title = title,
            description = description,
            category = category,
            pubDate = pubDate,
        )
        liste_totale.append(dictionnaire)
        
    # renvoie la liste de dico d'items
    return liste_totale



def with_feedparser(chemin):
    # lecture du nom du fichier
    nom_fichier = os.path.basename(chemin)
    
    # création de la future liste de dictionnaire d'item
    liste_items = []
    
    # récupération de la structure xml du document en chemin
    fichier = feedparser.parse(chemin)
    
    # on récupère toutes les balises item 
    items = fichier.entries
    
    # on récupère toutes les données et métadonnées des balises item
    for item in items:
        # initialisation du dictionnaire contenant les information d'un item
        dic_data = Item(
            source="", 
            title="", 
            description="", 
            category=[], 
            pubDate=""
            )
        dic_data.source = nom_fichier
        dic_data.title = item.title
        if hasattr(item, "summary"):
            dic_data.description = item.summary
        else:
            dic_data.description = None
        if hasattr(item, "published"):
            dic_data.pubDate = item.published
        else:
            dic_data.pubDate = None
        if hasattr(item, "tags"):
            dic_data.category = item.tags[0]["term"].split(", ")
        else:
            dic_data.category = None
        liste_items.append(dic_data)
        
    # on retourne la liste de dictionnaires
    return liste_items