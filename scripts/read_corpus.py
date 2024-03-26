'''
LES EXEMPLES D'UTILISATION :


POUR LE PIPE 
python3 read_corpus.py -o parcours -m et -cat "Transferts" -f xml  ./corpus --stdout | python3 analyzers.py --output ./output.xml --method trankit --stdin --f xml

Filter par catégorie 'Athlétisme' et enregistrer au format XML
python3 main.py -o parcours -m et -cat "Athlétisme" -f xml -s ./test_save.xml ./2024

Charger les résultats filtrés, enregistrés dans un fichier au format XML:
python3 main.py -o load -f xml ./test_save.xml

!!! IMPORTANT : assurez-vous d'avoir le fichier test_save dans le format approprié avant d'exécuter les exemples suivants

Charger les résultats du filtrage à partir du fichier au format XML, annoter avec Trankit et enregistrer au format JSON:
python3 main.py -o load -f xml ./test_save.xml --method_annote trankit -s ./annot_corpus.json

Charger les résultats filtrés depuis un fichier au format XML, les annoter avec Spacy, puis les sauvegarder au format XML:
python3 main.py -o load -f xml ./test_save.xml --method_annote spacy -s ./annot_corpus.xml

Charger les résultats filtrés depuis un fichier au format XML, les annoter avec Stanza, puis les sauvegarder au format JSON:
python3 main.py -o load -f xml ./test_save.xml --method_annote stanza -s ./annot_corpus.xml

'''

import argparse
import sys
import rss_reader
import rss_parcours
import datastructures
from pathlib import Path
from analyzers import all_items_trankit, all_items_spacy, all_items_stanza, save_corpus, load_corpus
import sys


def parse_files(file, role):
    """
        Choix de la méthode en fonction de l'argument donné lors du lancement du programme depuis le terminal.
        Prend en entré le fichier xml et la méthode utilisée.
    """
    if role == "re":
        return rss_reader.with_re(file)
    elif role == "et":
        return rss_reader.with_et(file)
    elif role == "fp":
        return rss_reader.with_feedparser(file)

def main():
    parser = argparse.ArgumentParser(prog="Récupérateur d'arguments")
    parser.add_argument("Path", type=str)
    parser.add_argument("-o", "--order", dest="order", help="Choix des ordres", type=str, choices=["reader", "parcours", "load"])
    parser.add_argument("-m", "--method", dest="method", help="Choix de la methode", type=str, choices=["re", "et", "fp"])
    parser.add_argument('-dd', '--date_debut', help='Heure de début.', required=False)
    parser.add_argument('-df', '--date_fin', help='Heure de fin.', required=False)
    parser.add_argument('-src', '--source', help='Source de l\'article.', required=False)
    parser.add_argument('-cat', '--category', help='Catégorie de l\'article.', required=False)
    parser.add_argument("-f", "--format", dest="format", help="Choix du format pour sauvegarder et recharger", type=str, choices=["xml", "json", "pickle"], required=False)
    parser.add_argument('-s', '--savePath', type=str, required=False)
    parser.add_argument("--stdout", action='store_true', help="Permet de faire passer le résultat du programme dans analyzers.py")
    args = parser.parse_args()

    if not args.order:
        sys.exit("Erreur : Il faut indiquer un ordre: reader ou parcours.")

    else:
        chemin = args.Path
        method = args.method

        if args.order == "reader":
            if args.method:
                corpus_items = parse_files(chemin, method)
                #print(corpus_items)
            else:
                sys.exit("Erreur : Il faut indiquer une methode de parsing.")

        elif args.order == "parcours":
            filtres = {}
            filtres["categories"] = []
            filtres["source"] = ''
            filtres["date"] = ['','']
            if args.date_debut:
                filtres["date"][0] = args.date_debut
            if args.date_fin:
                filtres["date"][1] = args.date_fin
            if args.source:
                filtres["source"] = args.source
            if args.category:
                categories = args.category.split()
                for category in categories:
                    filtres["categories"].append(category)

            corpus = rss_parcours.parcours_arborescence(chemin, method, filtres)
    
            if args.savePath: 
                chemin_save = args.savePath
 
                if args.format == "xml":
                    corpus = datastructures.save_xml(corpus, chemin_save)
                elif args.format == "json":
                    corpus = datastructures.save_json(corpus, chemin_save)
                elif args.format == "pickle":
                    corpus = datastructures.save_pickle(corpus, chemin_save)

            elif args.stdout:
                if args.format == "xml":
                    corpus = datastructures.save_xml(corpus, sys.stdout)
                    # print(corpus)
                elif args.format == "json":
                    corpus = datastructures.save_json(corpus, sys.stdout)
                elif args.format == "pickle":
                    corpus = datastructures.save_pickle(corpus, sys.stdout)


        elif args.order == "load":
            if not args.format:
                sys.exit("Erreur : Il faut indiquer un format pout recharger: xml, json ou pickle.")
            elif args.format == "xml":
                corpus = load_corpus(chemin)
                #print(corpus)
            elif args.format == "json":
                corpus = load_corpus(chemin)
                print(corpus)
            elif args.format == "pickle":
                corpus = load_corpus(chemin)
                print(corpus)

if __name__ == "__main__":
    main()
