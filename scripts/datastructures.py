from dataclasses import dataclass
from typing import List
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import fromstring
from pathlib import Path
import json
import pickle
import sys


@dataclass
class Item:
    source: str
    title: str
    description: str
    category: List[str]
    pubDate: str
    analysis: List[str] = None

@dataclass
class Corpus:
    items: List[List[Item]]

@dataclass
class Token:
    Form: str
    Lemma: str
    POS : str
    Gouv_lemme: str
    Gouv_pos: str
    Rel: str

    def to_dict(self):
        return {
            'Form': self.Form,
            'Lemma': self.Lemma,
            'POS': self.POS,
            'Gouv_lemme': self.Gouv_lemme,
            'Gouv_pos' : self.Gouv_pos,
            'Rel': self.Rel
        }



@dataclass
class Patron:
    dep_lemme: str
    dep_pos: str
    gouv1_lemme: str
    gouv1_pos: str
    role1: str
    gouv2_lemme: str
    gouv2_pos: str
    role2: str



def save_xml(corpus: Corpus, output_file) -> None:
    root = ET.Element("corpus")

    for item_list in corpus.items:
        item_list_elem = ET.SubElement(root, "itemList")
        for item in item_list:
            item_elem = ET.SubElement(item_list_elem, "item")
            source_elem = ET.SubElement(item_elem, "source")
            source_elem.text = item.source
            title_elem = ET.SubElement(item_elem, "title")
            title_elem.text = item.title
            description_elem = ET.SubElement(item_elem, "description")
            description_elem.text = item.description
            category_elem = ET.SubElement(item_elem, "category")
            category_elem.text = ",".join(item.category)
            pubDate_elem = ET.SubElement(item_elem, "pubDate")
            pubDate_elem.text = item.pubDate
            if item.analysis:
                analysis_elem = ET.SubElement(item_elem, "analysis")
                for token in item.analysis:
                    token_elem = ET.SubElement(analysis_elem, "token")
                    for key, value in token.to_dict().items():
                        sub_elem = ET.SubElement(token_elem, key)
                        sub_elem.text = value

    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0)
    
    if output_file == sys.stdout:
        print(ET.tostring(root, encoding='unicode'))
    else:
        tree.write(output_file, encoding="utf-8", xml_declaration=True)

def load_xml(input_file: str) -> Corpus:

    items = []
    if input_file == sys.stdin:
        donnees = input_file.read()
        root = fromstring(donnees)
    else:     
        root = ET.parse(input_file).getroot()

    for item_list_elem in root.findall("itemList"):
        item_list = []
        for item_elem in item_list_elem.findall("item"):
            source = item_elem.find("source").text
            title = item_elem.find("title").text
            description = item_elem.find("description").text
            category = item_elem.find("category").text.split(",")
            pubDate = item_elem.find("pubDate").text
            analysis = []
            if item_elem.find("analysis") is not None:
                for token_elem in item_elem.findall("analysis/token"):
                    token_dict = {elem.tag: elem.text for elem in token_elem}
                    analysis.append(Token(**token_dict))
            item_list.append(Item(source=source, title=title, description=description, category=category, pubDate=pubDate, analysis=analysis))
        items.append(item_list)

    return Corpus(items=items)

def save_json(corpus: Corpus, output_file: str) -> None:
    dico_data = dict()
    i = 0
    for items in corpus.items:
        i += 1
        file_data = []
        for item in items:
            analysis_data = [token.to_dict() for token in item.analysis] if item.analysis else None
            file_data.append({
                "source": item.source,
                "title": item.title,
                "description": item.description,
                "category": item.category,
                "pubDate": item.pubDate,
                "analysis": analysis_data
            })
        dico_data["file_" + str(i)] = file_data
        
    if output_file == sys.stdout:  
        print(json.dumps(dico_data, indent=4))
    else:
        with open(output_file, "w") as fichier_sorti:
            json.dump(dico_data, fichier_sorti, indent=4)

def load_json(input_file: str) -> Corpus:
    if input_file == sys.stdin:  
        json_object = json.load(sys.stdin)
    else:
        with open(input_file, "r") as openfile:
            json_object = json.load(openfile)

    corpus = Corpus(items=[])
    for key, items_list in json_object.items():
        items = []
        for item in items_list:
            analysis = [Token(**token_dict) for token_dict in item.get('analysis', [])]
            items.append(Item(
                source=item['source'],
                title=item['title'],
                description=item['description'],
                category=item['category'],
                pubDate=item['pubDate'],
                analysis=analysis
            ))
        corpus.items.append(items)

    return corpus

def save_pickle(corpus: Corpus, output_file) -> None:
    if output_file == sys.stdout:
       pickle.dump(corpus, sys.stdout.buffer)
    else:
        with open(output_file, 'wb') as file:
            pickle.dump(corpus, file)

def load_pickle(input_file: Path) -> Corpus:
    if input_file == sys.stdin:
        corpus = pickle.load(sys.stdin.buffer)
    else:
        with open(input_file, 'rb') as file:
            corpus = pickle.load(file)
    for item_list in corpus.items:
        for item in item_list:
            if hasattr(item, 'analysis') and item.analysis is not None:
                item.analysis = [Token(**token_dict) for token_dict in item.analysis]
    return corpus
