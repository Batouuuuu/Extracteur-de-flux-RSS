# -*- coding: utf-8 -*-
'''
Ce script prend en entrée un fichier de corpus précédemment sauvegardé,
analyse chaque Item de ce Corpus à l'aide de Trankit, Spacy ou Stanza, puis enregistre le corpus annoté
dans un fichier de sortie au format json, xml ou pickle.

Comment l'utiliser:
python3 analyzers.py <input_file> --output <output_file> --method <method>

à remplacer :
- <input_file> par le chemin vers votre corpus au format xml, pickle ou json
- <output_format> par le nom du fichier d'output au format xml, pickle ou json
- <method> par "trankit", "spacy" ou "stanza"
)
'''


import sys
import json
import pickle
import xml.etree.ElementTree as ET
import trankit
from trankit import Pipeline as PipelineTrankit
import spacy
import stanza
from stanza import Pipeline as PipelineStanza
from tqdm import tqdm
from datastructures import Corpus, Token, Item, load_xml, load_json, load_pickle, save_json, save_xml, save_pickle
from typing import List
import argparse
import re
from pathlib import Path




def annotate_spacy(item: Item) -> Item:
    nlp = spacy.load("fr_core_news_sm")
    texte_item = item.title + "." + item.description
    doc = nlp(texte_item)
    annotated_tokens = []
    for token in doc:
        token_form = token.text
        token_lemma = token.lemma_
        token_pos = token.pos_
        token_gouv_lemme = token.head.lemma_
        # print(token_gouv_lemme)
        token_gouv_pos = token.head.pos_
        token_rel = token.dep_
        annotated_token = Token(Form=token_form, Lemma=token_lemma, POS=token_pos, Gouv_lemme=token_gouv_lemme, Gouv_pos=token_gouv_pos, Rel=token_rel)
        annotated_tokens.append(annotated_token)
    annotated_item = Item(
        source=item.source,
        title=item.title,
        description=item.description,
        category=item.category,
        pubDate=item.pubDate,
        analysis=annotated_tokens
    )
    return annotated_item


def item_trankit(item: Item, nlp) -> Item:
    text = item.title + ". " + item.description
    annotations = nlp(text)
    tokens = []
    for sentence in annotations['sentences']:
        for token in sentence['tokens']:
            form = token['text']
            lemma = token.get('lemma', '')
            pos = token.get('upos', '')
            head = token.get('head', '')
            head_verif = None  ##important sinon erreur variable innaccesible
            Gouv_lemme = None  ##important sinon erreur variable innaccesible
            
            for token___hhead in sentence.get('tokens', ''):    ## parcours de tous les head
                if token___hhead['id'] == head: ## si id du token == [index] du gouveneur avec token head
                    head_verif = token___hhead.get('upos', '')  ###il faut prendre le pos
                    Gouv_lemme = token___hhead.get('lemma', '')
            deprel = token.get('deprel', '')
            tokens.append(Token(Form=form, Lemma=lemma, POS=pos, Gouv_lemme=Gouv_lemme, Gouv_pos=head_verif, Rel=deprel))
    return Item(source=item.source, title=item.title, description=item.description,
	category=item.category, pubDate=item.pubDate, analysis=tokens)


def annotate_stanza(item: Item, nlp) -> Item:
    text = item.title + "." + item.description
    doc = nlp(text)
    annotated_tokens = []
    for sentence in doc.sentences:
        for word in sentence.words:

            Form=word.text,
            Lemma=word.lemma,
            POS=word.pos,
            Gouv_lemme = sentence.words[word.head-1].text if word.head > 0 else word.text,
            id_head = word.head
            head_mot = sentence.words[id_head-1]
            Gouv_pos = head_mot.pos
            Rel = word.deprel
            annotated_token = Token(Form=Form, Lemma=Lemma, POS=POS, Gouv_lemme=Gouv_lemme, Gouv_pos=Gouv_pos, Rel=Rel)
            annotated_tokens.append(annotated_token)
    annotated_item = Item(
        source=item.source,
        title=item.title,
        description=item.description,
        category=item.category,
        pubDate=item.pubDate,
        analysis=annotated_tokens
    )
    return annotated_item


def all_items_stanza(corpus: Corpus, nlp) -> Corpus:
    corpus_annotated = Corpus(items=[])
    for item_list in corpus.items:
        annotated_item_list = []
        for item in item_list:
            annotated_item = annotate_stanza(item, nlp)
            annotated_item_list.append(annotated_item)
        corpus_annotated.items.append(annotated_item_list)
    return corpus_annotated


def all_items_trankit(corpus: Corpus, nlp) -> Corpus:
    annotated_corpus = Corpus(items=[])
    for item_list in corpus.items:
        annotated_item_list = [item_trankit(item, nlp) for item in item_list]
        annotated_corpus.items.append(annotated_item_list)
    return annotated_corpus


def all_items_spacy(corpus):
    corpus_annote = Corpus(items=[])
    for item_list in tqdm(corpus.items):
        annotated_item_list = []
        for item in item_list:
            annotated_item = annotate_spacy(item)
            annotated_item_list.append(annotated_item)
        corpus_annote.items.append(annotated_item_list)
    return corpus_annote


def load_corpus(file_path):
    file_extension = Path(file_path).suffix.lower()
    if file_extension == '.json':
        return load_json(file_path)
    elif file_extension == '.xml':
        return load_xml(file_path)
    elif file_extension == '.pkl':
        return load_pickle(file_path)
    else:
        raise ValueError("Le format n'est pas correct\n")


def save_corpus(corpus, output_file):
    file_extension = Path(output_file).suffix.lower()
    if file_extension == '.json':
        save_json(corpus, output_file)
    elif file_extension == '.xml':
        save_xml(corpus, output_file)
    elif file_extension == '.pkl':
        save_pickle(corpus, output_file)
    else:
        raise ValueError("Le format n'est pas correct\n")


def main():
    parser = argparse.ArgumentParser(description='Annote un corpus selon la méthode choisie')
    parser.add_argument('--file', type=str, help='Fichier contenant le corpus.', required=False)
    parser.add_argument("--output", default='ex.json', help="Choix du nom de fichier créé pour la sauvegarde du corpus filtré.")
    parser.add_argument("--method", default='spacy', help="Méthode d'annotation à utiliser (trankit, stanza ou spacy)")
    parser.add_argument("--stdin", action='store_true', help="ok")
    parser.add_argument("--f", choices=['xml','json','pkl'], help="ok.")
    args = parser.parse_args()

    if args.file:
        xml_pattern = r'\.xml$'
        json_pattern = r'\.json$'
        pickle_pattern = r'\.pkl$'
        if re.search(xml_pattern, corpus):
            corpus = load_xml(corpus)
        elif re.search(json_pattern, corpus):
            corpus = load_json(corpus)
        elif re.search(pickle_pattern, corpus):
            corpus = load_pickle(corpus)
        else:
            print("Format non reconnu")

    elif args.stdin:
        if args.f == 'xml':
            corpus = load_xml(sys.stdin)
        elif args.f == 'json':
            corpus = load_json(sys.stdin)
        elif args.f == 'pkl':
            corpus = load_pickle(sys.stdin)
        else:
            print("Format non reconnu")


    if args.method == 'trankit':
        nlp = PipelineTrankit('french')
        corpus_annote = all_items_trankit(corpus, nlp)
    elif args.method == 'spacy':
        corpus_annote = all_items_spacy(corpus)
    elif args.method == 'stanza':
        nlp = PipelineStanza('fr')
        corpus_annote = all_items_stanza(corpus, nlp)
    else:
        print("Méthode d'annotation non reconnue")
        return

    if args.output:
        output_file = args.output
        save_corpus(corpus_annote, output_file)

if __name__ == "__main__":
    main()
