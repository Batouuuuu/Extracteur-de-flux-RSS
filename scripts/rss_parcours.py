from pathlib import Path
from typing import List, Dict
import datetime
import rss_reader
from datastructures import Item, Corpus

"""
Ici les fonctions utilisées pour parcourir l'arborescence, et filtrer les documents retournés (semaine 5):
- filtre_dates pour filtrer selon des dates (r1)
- filtre_source pour filtrer selon des sources (r2)
- filtre_categories pour filtrer selon des categories (r3)
Et une fonction pour les appeler : check_filtres() qui va vérifier chacun des
filtres et retourner une liste ne contenant que les fichiers demandés.
- des fonctions complémentaires à celles des filtres (dont les filtres ont besoin)
- une fonction load_corpus pour charger un corpus 
- une fonction parcours_arborescence qui permettra de parcourir l'arborescence et d'afficher, 
    selon les filtres (fournis par l'utilsateur, et qui serviront de paramètres à la fonction), les articles correspondants  
"""


def load_corpus(path: str):
    current = Path(path)
    return current.rglob("*.xml")   # On va devoir retourner un corpus



def check_filtres(corpus: List[List[Item]], filtres: Dict) -> Corpus:
    if not filtres["categories"] and not filtres["date"] and not filtres["source"]:
        return corpus
    filtered = Corpus(items=[])
    for file in corpus:
        items = []
        for item in file:
            if filtre_categories(item, filtres["categories"]) and filtre_date(item, filtres["date"]) and filtre_source(item, filtres["source"]):
                items.append(item)
        if items:
            filtered.items.append(items)
    return filtered

# Role 1 s5
def filtre_date(item: Item, user_dates: List[str]) -> bool:
    """
    Cette fonction normalise les dates des fichiers, récupère les dates fournies par l'utilisateur,
    et sélectionne les fichiers dont la date de publication est comprise entre les dates spécifiées par l'utilisateur.
    """
    if not user_dates[0] and not user_dates[1]:
        return True
    if not item.pubDate:
        return False
    date_normalisee = normaliser_date(item)
    date_debut, date_fin = date_utilisateur(user_dates)
    statut_date = selection_date(date_normalisee, date_debut, date_fin)
    return statut_date

def normaliser_date(item: Item) -> Item:
    """
    Cette fonction permet de normaliser le format de date pour tous les fichiers. Transforme la date en objet datetime pour pouvoir l'utiliser plus tard.
    """
    # liste des 3 formats possibles trouvés dans les fichiers
    formats = [
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%S%z",
    ]
    pubDate = item.pubDate
    # transformation de la date -> essai sur les 3 formats possibles
    for format_date in formats:
        try:
            pubDatetime = datetime.datetime.strptime(pubDate, format_date)
            formatOK = pubDatetime.date()
            item.pubDate = formatOK  # nouvelle date dans le dico
            break
        except ValueError:
            continue
    return item     # On va devoir retourner un objet item


def date_utilisateur(user_dates:List[str]):
    """
    Cette fonction récupère la/les dates entrées par l'utilisateur afin de la/les transformer en objet datetime pour pouvoir l'utiliser plus tard.
    """
    date_debut = None
    date_fin = None
    if user_dates[0]:
        date_debut = datetime.datetime.strptime(user_dates[0], "%Y-%m-%d").date()
    if user_dates[1]:
        date_fin = datetime.datetime.strptime(user_dates[1], "%Y-%m-%d").date()
    return date_debut, date_fin


def selection_date(item, date_debut, date_fin):
    """
    Cette fonction sélectionne les fichiers dont la date de publication est comprise entre la date de début et la date de fin (si spécifiées) par l'utilisateur.
    Si seulement date de début, on sélectionne les fichiers après cette date.
    Si seulement date de fin, on sélectionne les fichiers avant cette date.
    """
    date_article = item.pubDate
    if not date_debut and not date_fin:
        return True
    if date_debut and date_fin:
        return date_debut <= date_article <= date_fin
    if date_debut:
        return date_debut <= date_article
    if date_fin:
        return date_fin >= date_article
    return False

# Rôle 2 s5
def filtre_source(item: Item, source) -> bool:
    if not source:
        return True
    if not item.source:
        return False
    if source.lower() in str(item.source).lower():
        return True
    return False

# Rôle 3 s5
def filtre_categories(item: Item, categories: list) -> bool:
    if not categories:
        return True
    if not item.category:
        return False
    for category in categories:
        if category.lower() in [cat.lower() for cat in item.category]:
            return True
    return False


# NGAUV Nicolas s6

def parse_files(files, method):
    parsed_corpus = []
    for file in files:
        if method == "re":
            parsed_corpus.append(rss_reader.with_re(file))
        if method == "et":
            parsed_corpus.append(rss_reader.with_et(file))
        if method == "fp":
            parsed_corpus.append(rss_reader.with_feedparser(file))
    return parsed_corpus

def parcours_arborescence (chemin, method, filtres):    # Objet corpus à la place de chemin ?
    files = load_corpus(chemin)
    parsed_corpus = parse_files(files, method)
    """
    Maintenant fournis par l'utilisateur et donc gérés dans le main
    filtres = {
        "categories": args.filtre_category,
        "date": [args.date_debut, args.date_fin],
        "source": args.filtre_source
    }
    """
    data = check_filtres(parsed_corpus, filtres)
    # for file in data.items:
    #     for item in file:
            #print(f"date : {item['pubDate']}, category : {item['category']}, source = {item['source']}")
            # print(f"titre : {item.title}, description : {item.description}, date = {item.pubDate}, categories : {item.category}")
    return data