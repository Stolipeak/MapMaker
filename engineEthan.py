from fltk import *
import os


cree_fenetre(960, 540)

print(os.listdir("tuiles"))

def cree_dico(chemin):
    dico = {}
    for nom in os.listdir(chemin):
        if nom.endswith(".png"):
            dico[os.path.splitext(nom)[0]] = chemin + "/" + nom
    return dico

def noOutOfRange(grille, i, j, nom, dico):
    positions_possibles = []
    if i < 0 or i >= len(grille) or j < 0 or j >= len(grille[0]):
        return False  # La case actuelle est hors des limites
    voisins = [
        (i - 1, j),  # Haut
        (i + 1, j),  # Bas
        (i, j - 1),  # Gauche
        (i, j + 1)   # Droite
    ]
    for vi, vj in voisins:
        if 0 <= vi < len(grille) and 0 <= vj < len(grille[0]):
            positions_possibles.append((vi, vj))  # Ajoute les positions valides
    return positions_possibles
grille = [[None for _ in range(10)] for _ in range(10)]
print(grille)


dico = cree_dico("tuiles")
while True:
    ev = attend_ev()
    tev = type_ev(ev)
    if tev == "CliqueGauche":
        pass
    elif tev == "Quitte":
        break
    mise_a_jour()
ferme_fenetre()