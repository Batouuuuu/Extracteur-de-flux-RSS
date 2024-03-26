from datastructures import Item, Patron, load_xml, load_json, load_pickle, Corpus
import argparse
from typing import List
import csv
from tabulate import tabulate



# Lancement du script :
# python3 patterns.py corpus_annote.xml analyse_patrons.csv

# corpus_annote.xml est un fichier contenant l'annotation obtenue avec analyzers.py
# analyse_patrons.csv est le fichier de sorite csv contenant les patrons extraits avec leurs instances et leurs comptes



def load_file(fichier) :
    if fichier.endswith(('.xml', '.json', '.pkl')):
        if fichier.endswith('.xml'):
            corpus_analyse = load_xml(fichier)
        elif fichier.endswith('.json'):
            corpus_analyse = load_json(fichier)
        elif fichier.endswith('.pkl'):
            corpus_analyse = load_pickle(fichier)
        return corpus_analyse
    else:
        print("Format de fichier non pris en charge. Vous devez fournir un fichier xml, json ou pkl")
        return



# 1. Patrons simples :

def N_obj_V(item: Item) -> List[Patron] :
    '''extrait les patrons du type "le chat mange la souris"'''
    patrons = []
    for token in item.analysis:
        if token.POS == 'NOUN' and token.Rel == 'obj':
            dependant_lemme = token.Lemma
            dependant_pos = token.POS
            head = token.Gouv_lemme
            for gouv in item.analysis:
                if gouv.Form == head and gouv.POS == 'VERB':
                    head_lemme = gouv.Lemma
                    head_pos = gouv.POS
                    patron = Patron(dependant_lemme, dependant_pos, head_lemme, head_pos, 'obj', '', '', '')
                    patrons.append(patron)
    return patrons



def V_nsubj_N(item: Item) -> List[Patron] :
    '''extrait les patrons du type "le chat mange la souris"'''
    patrons = []
    for token in item.analysis:
        if token.POS == 'NOUN' and token.Rel == 'nsubj':
            dependant_lemme = token.Lemma
            dependant_pos = token.POS
            head = token.Gouv_lemme
            for gouv in item.analysis:
                if gouv.Form == head and gouv.POS == 'VERB':
                    head_lemme = gouv.Lemma
                    head_pos = gouv.POS
                    patron = Patron(dependant_lemme, dependant_pos, head_lemme, head_pos, 'nsubj', '', '', '')
                    patrons.append(patron)
    return patrons



def nom_nmod_N(item: Item) -> List[Patron] :
    '''extrait les patrons du type "le chat mange la souris"'''
    patrons = []
    for token in item.analysis:
        if token.POS == 'NOUN' and token.Rel == 'nmod':
            dependant_lemme = token.Lemma
            dependant_pos = token.POS
            head = token.Gouv_lemme
            for gouv in item.analysis:
                if gouv.Form == head and gouv.POS == 'NOUN':
                    head_lemme = gouv.Lemma
                    head_pos = gouv.POS
                    patron = Patron(dependant_lemme, dependant_pos, head_lemme, head_pos, 'nmod', '', '', '')
                    patrons.append(patron)
    return patrons



# 2. Patrons complexes :

def ADP_mark_VERB_xcomp_VERB(item: Item) -> List[Patron] :
    '''extrait les patrons du type "il est invité à partir"'''
    patrons = []
    for token in item.analysis:
        if token.POS == "ADP" and token.Rel == "mark":
            dependant_lemme = token.Lemma
            dependant_pos = token.POS
            head1 = token.Gouv_lemme
            for gouv in item.analysis:
                if gouv.Form == head1 and gouv.POS == "VERB" and gouv.Rel == "xcomp" :
                    head1_lemme = gouv.Lemma
                    head1_pos = gouv.POS
                    head2 = gouv.Gouv_lemme
                    for gouv_du_gouv in item.analysis :
                        if gouv_du_gouv.Form == head2 and gouv_du_gouv.POS == "VERB" :
                            head2_lemme = gouv_du_gouv.Lemma
                            head2_pos = gouv_du_gouv.POS
                            patron = Patron(dependant_lemme, dependant_pos, head1_lemme, head1_pos, 'mark', head2_lemme, head2_pos, 'xcomp')
                            patrons.append(patron)
    return patrons



def CCONJ_cc_NOUN_conj_NOUN(item: Item) -> List[Patron] :
    '''extrait les patrons du type "il est invité à partir"'''
    patrons = []
    for token in item.analysis:
        if token.POS == "CCONJ" and token.Rel == "cc":
            dependant_lemme = token.Lemma
            dependant_pos = token.POS
            head1 = token.Gouv_lemme
            for gouv in item.analysis:
                if gouv.Form == head1 and gouv.POS == "NOUN" and gouv.Rel == "conj" :
                    head1_lemme = gouv.Lemma
                    head1_pos = gouv.POS
                    head2 = gouv.Gouv_lemme
                    for gouv_du_gouv in item.analysis :
                        if gouv_du_gouv.Form == head2 and gouv_du_gouv.POS == "NOUN" :
                            head2_lemme = gouv_du_gouv.Lemma
                            head2_pos = gouv_du_gouv.POS
                            patron = Patron(dependant_lemme, dependant_pos, head1_lemme, head1_pos, 'cc', head2_lemme, head2_pos, 'conj')
                            patrons.append(patron)
    return patrons



def all_patterns(corpus: Corpus) -> List[Patron] :
    '''extrait tous les patrons du corpus'''
    tous_les_patrons = []
    for item_list in corpus.items:
        for item in item_list:
            patrons_nom_nmod_N = nom_nmod_N(item)
            patrons_N_obj_V = N_obj_V(item)
            patrons_V_nsubj_N = V_nsubj_N(item)
            patron_mark_xcomp = ADP_mark_VERB_xcomp_VERB(item)
            patron_conjcoord = CCONJ_cc_NOUN_conj_NOUN(item)
            tous_les_patrons.extend(patrons_V_nsubj_N)
            tous_les_patrons.extend(patrons_nom_nmod_N)
            tous_les_patrons.extend(patrons_N_obj_V)
            tous_les_patrons.extend(patron_mark_xcomp)
            tous_les_patrons.extend(patron_conjcoord)
    return tous_les_patrons



def patron_to_string(liste_patrons: List[Patron]) -> List[str] :
    '''convertit une liste de patrons en liste de strings triée'''
    patrons_string = []
    for patron in liste_patrons :
        patstr = str(patron.dep_pos)+", "+str(patron.dep_lemme)+", "+str(patron.role1)+", "+str(patron.gouv1_pos)+", "+str(patron.gouv1_lemme)+", "+str(patron.role2)+", "+str(patron.gouv2_pos)+", "+str(patron.gouv2_lemme)
        patrons_string.append(patstr)
    patrons_string = sorted(patrons_string)
    return patrons_string



def compte_instances(liste_patrons_string: List[str]) -> List[str] :
    '''compte le nombre de fois où un patron apparraît'''
    occurrences = {}
    for patron in liste_patrons_string :
        if patron in occurrences :
            occurrences[patron] += 1
        else :
            occurrences[patron] = 1
    patrons_occ = []
    for pat in occurrences :
        pat_str = pat + ", " + str(occurrences[pat])
        patrons_occ.append(pat_str)
    return patrons_occ



def ecriture_csv(fichier, liste_patrons) :
    '''écrit une liste de patrons sous forme de strings dans un fichier csv'''
    with open(fichier, 'w', newline='', encoding='utf-8') as fichier_csv:
        champs = ['dep', 'gouv', 'role1', 'gouverneur_du_gouverneur', 'role2', 'compte']
        ecrire = csv.DictWriter(fichier_csv, fieldnames=champs)

        ecrire.writeheader()
        #for patron in patrons_finaux :
        for patron in liste_patrons :
            ecrire.writerow({
            'dep': patron[1],
            'gouv': patron[4],
            'role1': patron[2],
            'gouverneur_du_gouverneur': patron[7],
            'role2': patron[5],
            'compte' : patron[8]
            })



def tableau (liste_patrons: List[List[str]]) :
    '''affiche les patrons simples sous forme d'un tableau'''
    patrons_simples = []
    for patron in liste_patrons :
        if patron[5] == '' :
            patron = [patron[0], patron[1], patron[2], patron[3], patron[4], patron[8]]
            print(patron)
            patrons_simples.append(patron)
    entetes = ['pred_cat', 'pred_lemme', 'pred_rel', 'arg_cat', 'arg_lemme', 'freq']
    print(tabulate(patrons_simples, headers=entetes))



def main() :
    # Gérer les arguments
    parser = argparse.ArgumentParser(description="Extraction des patron.")
    parser.add_argument("input_file", type=str, help="Chemin du fichier d'analyse")
    parser.add_argument("output_file", type=str, help="Chemin vers le fichier de sortie CSV")
    args = parser.parse_args()

    # Identifier le format du fichier d'analyse pour appliquer la bonne fonction de lecture
    corpus_analyse = load_file(args.input_file)

    # Extraire tous les patrons
    tous_les_patrons = all_patterns(corpus_analyse)

    # Trier les patrons et compter les instances de chaque patron
    tous_les_patrons_str = patron_to_string(tous_les_patrons)
    patrons_avec_comptes = compte_instances(tous_les_patrons_str)

    # Convertir tous les patrons sous forme d'une liste de listes de str
    liste_patrons = []
    for patron_str in patrons_avec_comptes :
        patron_liste = patron_str.split(", ")
        liste_patrons.append(patron_liste)

    # Afficher les patrons simples en tableau
    tableau(liste_patrons)

    # Ecrire les patrons dans un fichier csv
    ecriture_csv(args.output_file, liste_patrons)



if __name__ == "__main__":
    main()
