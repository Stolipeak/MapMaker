from fltk import *
import os


cree_fenetre(960, 540)


def cree_dico(chemin):
    dico = {}
    for nom in os.listdir(chemin):
        if nom.endswith(".png"):
            dico[os.path.splitext(nom)[0]] = chemin + "/" + nom
    return dico

def noOutOfRange(grille, i, j, nom, dico):
    positions_possibles = {}
    if i < 0 or i >= len(grille) or j < 0 or j >= len(grille[0]):
        return False  # La case actuelle est hors des limites
    voisins = {
        "Haut": (i - 1, j),
        "Bas": (i + 1, j),
        "Gauche": (i, j - 1),
        "Droite": (i, j + 1)
    }
    for direction, (vi, vj) in voisins.items():
        if 0 <= vi < len(grille) and 0 <= vj < len(grille[0]):
            positions_possibles[direction] = (vi, vj)  # Ajoute les positions valides avec direction
    return positions_possibles


def emplacement_valide(grille, i, j, nom, dico):
    positions_possibles = noOutOfRange(grille, i, j, nom, dico)
    for posName in positions_possibles:
        nomGrille = grille[positions_possibles[posName][0]][positions_possibles[posName][1]]
        if posName == "Haut":
            if nomGrille[2]  != nom[0]:
                return False
        elif posName == "Droite":
            if nomGrille[3] != nom[1]:
                return False
        elif posName == "Bas":
            if nomGrille[0] != nom[2]:
                return False
        else:
            if nomGrille[1] != nom[3]:
                return False
    return True

dico = cree_dico("tuiles")
grille = [[None for _ in range(10)] for _ in range(10)]
grille[0][1] = "FFFM"
grille[1][0] = "FFMF"
grille[2][1] = "FFFM"
grille[1][2] = "FFMF"
for g in grille:
    print(g)

print(emplacement_valide(grille, 1, 1, "FFFF", dico))

while True:
    ev = attend_ev()
    tev = type_ev(ev)
    if tev == "CliqueGauche":
        pass
    elif tev == "Quitte":
        break
    mise_a_jour()
ferme_fenetre()