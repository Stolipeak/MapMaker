from fltk import *
import os
import random
import winsound

# paramètres de base
TAILLE_CASE = 64
NB_CASES = 10
LARGEUR_FENETRE = NB_CASES * TAILLE_CASE
HAUTEUR_FENETRE = NB_CASES * TAILLE_CASE
LARGEUR_BARRE = 200  # Largeur de la barre latérale
LARGEUR_TOTALE = LARGEUR_FENETRE + LARGEUR_BARRE

# dico pour mieux comprendre les lettres sur les tuiles
COTES = {
    'F': 'Forêt',
    'M': 'Montagne',
    'P': 'Plaine',
    'R': 'Rivière',
    'S': 'Mer',
    'D': 'Côte droite',
    'G': 'Côte gauche',
    'B': 'Bas de côte',
    'H': 'Haut de côte'
}


class MapMaker:
    def __init__(self):
        # la grille sera une liste de listes, initialement vide
        self.grille = [[None for _ in range(NB_CASES)] for _ in range(NB_CASES)]
        self.tuiles = self.charger_tuiles("tuiles")
        self.selection = None
        self.menuVisible = False
        self.position_menu = (0, 0)
        self.choixPossibles = []
        self.caseChoisie = None
        self.message_status = ""  # Message de statut
        self.timer_status = 0  # Compteur pour le message
        self.couleur_status = "green"  # Couleur par défaut du message
        self.menu = "acc"
        # Attributs pour la navigation
        self.indice = 0
        self.nbPages = 0

    def setMenu(self):
        if self.menu == "acc":
            cree_fenetre(600, 600)
            efface_tout()
            # Lancer la musique au démarrage
            winsound.PlaySound("media/nouveauTheme.wav", winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)
            # Background
            rectangle(0, 0, 600, 600, couleur='sky blue', remplissage='sky blue')

            cloud_positions = [
                (20, 20), (100, 50), (200, 100), (300, 150), (400, 200),
                (500, 250), (50, 300), (150, 350), (250, 400), (350, 450),
                (450, 500), (550, 50), (20, 550), (100, 500), (200, 450),
                (300, 400), (400, 350), (500, 300), (50, 200), (150, 100),
                (250, 50), (350, 20), (450, 100), (550, 200), (20, 300),
                (100, 400), (200, 500), (300, 550), (400, 500), (500, 400),
                (50, 150), (150, 50), (250, 20), (350, 100), (450, 200),
                (550, 300), (20, 400), (100, 450), (200, 550), (300, 500),
                (400, 450), (500, 350), (50, 250), (150, 200), (250, 150),
                (350, 50), (450, 20), (550, 100), (20, 200), (100, 300)
            ]

            # Dessiner les nuages
            for x, y in cloud_positions:
                image(x, y, "media/cloud.png", largeur=80, hauteur=80, ancrage='nw')

            # Logo et boutons
            image(300, 100, "media/logoMM.png", largeur=300, hauteur=300, ancrage='center')

            # Bouton MapMaker
            rectangle(200, 290, 400, 340, couleur='black', remplissage='white', epaisseur=2)
            texte(300, 315, "MapMaker", couleur='black', taille=16, ancrage='center')

            # Bouton pour activer/désactiver le son
            rectangle(550, 2, 600, 52, couleur='black', remplissage='white', epaisseur=2)
            image(575, 27, "media/goSound.png", largeur=20, hauteur=20, ancrage='center', tag="isSound")
            isSound = True

            while True:
                ev = attend_ev()
                tev = type_ev(ev)
                if tev == 'Quitte':
                    break
                elif tev == 'ClicGauche':
                    x, y = abscisse(ev), ordonnee(ev)
                    if 200 <= x <= 400 and 340 >= y >= 290:
                        print("MapMaker")
                        self.menu = "MapMaker"
                        ferme_fenetre()  # Fermer la fenêtre d'abord
                        cree_fenetre(LARGEUR_TOTALE, HAUTEUR_FENETRE)  # Puis créer la nouvelle
                        self.boucle_principale()
                        return
                    elif 550 <= x <= 600 and 52 >= y >= 2:
                        if isSound:
                            isSound = False
                            winsound.PlaySound(None, winsound.SND_ASYNC)
                            efface("isSound")
                            image(575, 27, "media/stopSound.png", largeur=20, hauteur=20, ancrage='center',
                                  tag="isSound")
                        else:
                            isSound = True
                            winsound.PlaySound("media/nouveauTheme.wav",
                                               winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)
                            efface("isSound")
                            image(575, 27, "media/goSound.png", largeur=20, hauteur=20, ancrage='center', tag="isSound")
                            print("Reprise de la musique")

                    print(f"Clic gauche à ({x}, {y})")
                elif tev == 'ClicDroit':
                    x, y = abscisse(ev), ordonnee(ev)
                    print(f"Clic droit à ({x}, {y})")
                elif tev == 'Touche':
                    t = touche(ev)
                    print(f"Touche pressée : {t}")
                mise_a_jour()
            ferme_fenetre()
        else:
            # Si ce n'est pas le menu d'accueil, créez directement la fenêtre principale
            cree_fenetre(LARGEUR_TOTALE, HAUTEUR_FENETRE)
            self.boucle_principale()


    def charger_tuiles(self, dossier):
        # on scanne le dossier et on prend toutes les images de tuiles valides
        tuiles = {}
        if os.path.exists(dossier):
            for fichier in os.listdir(dossier):
                if fichier.endswith(".png"):
                    nom = fichier.split(".")[0]
                    if len(nom) == 4:
                        tuiles[nom] = os.path.join(dossier, fichier)
        return tuiles


    def case_ok(self, i, j, code):
        # regarde si une tuile peut être posée à la position (i, j)
        haut, droite, bas, gauche = code

        if i > 0 and self.grille[i - 1][j] is not None:
            if self.grille[i - 1][j][2] != haut:
                return False
        if j < NB_CASES - 1 and self.grille[i][j + 1] is not None:
            if self.grille[i][j + 1][3] != droite:
                return False
        if i < NB_CASES - 1 and self.grille[i + 1][j] is not None:
            if self.grille[i + 1][j][0] != bas:
                return False
        if j > 0 and self.grille[i][j - 1] is not None:
            if self.grille[i][j - 1][1] != gauche:
                return False

        return True

    def tuilesPossibles(self, i, j):
        # retourne toutes les tuiles qui iraient à cet endroit
        possibles = []
        for t in self.tuiles:
            if self.case_ok(i, j, t):
                possibles.append(t)
        return possibles

    def poser(self, i, j, code):
        # pose la tuile si elle va bien
        if self.case_ok(i, j, code):
            self.grille[i][j] = code
            return True
        return False

    def retirer(self, i, j):
        # retire une tuile d'une case
        self.grille[i][j] = None

    def remplir_auto(self):
        # tentative de remplir toute la carte
        vide = [(i, j) for i in range(NB_CASES) for j in range(NB_CASES) if self.grille[i][j] is None]
        if not vide:
            return True

        i, j = vide[0]
        essais = self.tuilesPossibles(i, j)

        for tuile in essais:
            self.grille[i][j] = tuile
            if self.remplir_auto():
                return True
            self.grille[i][j] = None  # raté, on revient en arrière

        return False

    def afficher_message_status(self, message, duree=100, couleur="green"):
        """Affiche un message de statut pour une durée donnée avec une couleur."""
        self.message_status = message
        self.timer_status = duree
        self.couleur_status = couleur

    def dessiner_message_status(self):
        """Dessine un rectangle en haut à droite qui reste toujours visible."""

        # Descendre le titre
        texte((LARGEUR_FENETRE + LARGEUR_TOTALE) // 2, 110, "Message Système",
              couleur='black', taille=14, ancrage='center', police='bold')

        # Descendre le rectangle
        rectangle(LARGEUR_FENETRE + 10, 140, LARGEUR_TOTALE - 10, 210, couleur='black', remplissage='white',
                  epaisseur=2)

        # Descendre le message
        if self.timer_status > 0:
            texte((LARGEUR_FENETRE + LARGEUR_TOTALE) // 2, 175, self.message_status,
                  couleur=self.couleur_status, taille=16, ancrage='center', police='bold')
            self.timer_status -= 1  # Réduit le compteur

    def dessiner(self):
        # affiche la grille de tuiles
        for i in range(NB_CASES):
            for j in range(NB_CASES):
                x = j * TAILLE_CASE
                y = i * TAILLE_CASE
                if self.grille[i][j] is not None:
                    chemin = self.tuiles[self.grille[i][j]]
                    image(x, y, chemin, largeur=TAILLE_CASE, hauteur=TAILLE_CASE, ancrage='nw')
                else:
                    rectangle(x, y, x + TAILLE_CASE, y + TAILLE_CASE, couleur='black', remplissage='light gray',
                              epaisseur=1)

        # Dessiner la barre latérale
        rectangle(LARGEUR_FENETRE, 0, LARGEUR_TOTALE, HAUTEUR_FENETRE, couleur='black', remplissage='white')
        image((LARGEUR_FENETRE + LARGEUR_TOTALE) // 2, 50, "media/logoMM.png", largeur=120, hauteur=120, ancrage='center')

        # Bouton "Ajout Décors"
        rectangle(LARGEUR_FENETRE + 10, HAUTEUR_FENETRE // 2 - 25, LARGEUR_TOTALE - 10, HAUTEUR_FENETRE // 2 + 25,
                  couleur='black', remplissage='white', epaisseur=2)
        texte((LARGEUR_FENETRE + LARGEUR_TOTALE) // 2, HAUTEUR_FENETRE // 2, "Ajout Décors",
              couleur='black', taille=16, ancrage='center')

        # Grand rectangle principal
        rectangle(650, 360, 830, 585, couleur="black", remplissage='white', epaisseur=2)
        # Lignes horizontales pour diviser en 6 rangées
        ligne(650, 405, 830, 405, couleur="black", epaisseur=1)  # 1ère ligne horizontale
        ligne(650, 450, 830, 450, couleur="black", epaisseur=1)  # 2ème ligne horizontale
        ligne(650, 495, 830, 495, couleur="black", epaisseur=1)  # 3ème ligne horizontale
        ligne(650, 540, 830, 540, couleur="black", epaisseur=1)  # 4ème ligne horizontale

    def dessiner_menu(self):
        if not self.menuVisible or not self.choixPossibles:
            return

        # Calculer la page actuelle et les indices
        page_actuelle = self.indice // 5  # Changé de 6 à 5
        debut = page_actuelle * 5  # Changé de 6 à 5
        fin = min(debut + 5, len(self.choixPossibles))  # Changé de 6 à 5

        # Afficher le numéro de page en haut du rectangle
        if self.nbPages > 1:
            texte(740, 352, f"Page {page_actuelle + 1}/{self.nbPages}",
                  couleur='black', taille=10, ancrage='center')

        # Calculer la hauteur de chaque section
        hauteur_section = (585 - 360) / 5  # Changé pour 5 sections

        # Afficher les tuiles
        for idx, position in enumerate(range(debut, fin)):
            if position < len(self.choixPossibles):
                code_tuile = self.choixPossibles[position]
                y_base = 360 + (idx * hauteur_section)
                y_centre = y_base + (hauteur_section / 2)

                texte(665, y_centre, code_tuile, couleur='black', taille=10, ancrage='w')

                if code_tuile in self.tuiles:
                    try:
                        image(795, y_centre, self.tuiles[code_tuile],
                              largeur=35, hauteur=35, ancrage='center')
                    except:
                        texte(795, y_centre, "?", couleur='red', taille=16, ancrage='center')

        # Flèches de navigation en bas du rectangle (gauche et droite)
        if self.nbPages > 1:
            # Flèche gauche (page précédente)
            if page_actuelle > 0:
                # Rectangle contenant la flèche gauche
                rectangle(660, 605, 710, 625, couleur="black", remplissage="lightgray")
                # Triangle pour la flèche
                polygone([(670, 615), (680, 605), (680, 625)], couleur="black", remplissage="black")

            # Flèche droite (page suivante)
            if page_actuelle < self.nbPages - 1:
                # Rectangle contenant la flèche droite
                rectangle(770, 605, 820, 625, couleur="black", remplissage="lightgray")
                # Triangle pour la flèche
                polygone([(810, 615), (800, 605), (800, 625)], couleur="black", remplissage="black")

    def afficheTuilesPossibles(self, i, j, bouton):
        """Prépare l'affichage des tuiles possibles pour une case donnée."""
        self.choixPossibles = self.tuilesPossibles(i, j)
        self.caseChoisie = (i, j)
        self.indice = 0  # Commence à la première page
        self.nbPages = (len(self.choixPossibles) + 4) // 5  # Changé de 6 à 5
        self.menuVisible = True

        if len(self.choixPossibles) > 0:
            self.afficher_message_status(f"Case ({j},{i}): {len(self.choixPossibles)} \n tuiles possibles",
                                         duree=200, couleur="green")
        else:
            self.afficher_message_status("Aucune tuile \n possible",
                                         duree=200, couleur="red")

    def gerer_clic(self, x, y, bouton):
        # clic gauche ou droit sur la grille
        i, j = y // TAILLE_CASE, x // TAILLE_CASE

        # Gestion des flèches de navigation dans le rectangle
        if self.menuVisible and bouton == 1:
            page_actuelle = self.indice // 6

            # Vérifier si le clic est sur une des flèches de navigation
            if 605 <= y <= 625:
                # Flèche gauche (précédent)
                if 660 <= x <= 710 and page_actuelle > 0:
                    self.indice = max(0, self.indice - 6)
                    return

                # Flèche droite (suivant)
                if 770 <= x <= 820 and page_actuelle < self.nbPages - 1:
                    self.indice = min(self.indice + 6, len(self.choixPossibles) - 1)
                    return

            # Dans la méthode gerer_clic()
            if 650 <= x <= 830 and 360 <= y <= 585:
                hauteur_section = (585 - 360) / 5  # Changé pour 5 sections
                section = int((y - 360) // hauteur_section)

                if 0 <= section < 5:  # Changé de 6 à 5
                    index_tuile = page_actuelle * 5 + section  # Changé de 6 à 5

                    if index_tuile < len(self.choixPossibles) and self.caseChoisie:
                        ci, cj = self.caseChoisie
                        code_tuile = self.choixPossibles[index_tuile]

                        if self.poser(ci, cj, code_tuile):
                            self.afficher_message_status(f"Tuile {code_tuile} posée", duree=100, couleur="green")
                        else:
                            self.afficher_message_status("Impossible de poser cette tuile", duree=100, couleur="red")

                        self.menuVisible = False
                        self.caseChoisie = None
                        return

        # Si le clic est sur la grille
        if 0 <= i < NB_CASES and 0 <= j < NB_CASES and x < LARGEUR_FENETRE:
            if bouton == 1:  # Clic gauche
                self.afficheTuilesPossibles(i, j, bouton)
            elif bouton == 3:  # Clic droit
                self.retirer(i, j)
                self.menuVisible = False
                self.caseChoisie = None


        # Si le clic est sur la grille
        if 0 <= i < NB_CASES and 0 <= j < NB_CASES and x < LARGEUR_FENETRE:
            if bouton == 1:  # Clic gauche
                self.afficheTuilesPossibles(i, j, bouton)
            elif bouton == 3:  # Clic droit
                self.retirer(i, j)
                self.menuVisible = False
                self.caseChoisie = None


        # Si le clic est sur la grille
        if 0 <= i < NB_CASES and 0 <= j < NB_CASES:
            if bouton == 1:  # Clic gauche
                self.caseChoisie = (i, j)
                self.afficheTuilesPossibles(i, j, bouton)
            elif bouton == 3:  # Clic droit
                self.retirer(i, j)
                self.menuVisible = False
                self.caseChoisie = None

    def boucle_principale(self):
        # tourne tant que la fenêtre est ouverte
        while True:
            efface_tout()
            self.dessiner()
            self.dessiner_menu()
            self.dessiner_message_status()  # Affiche le message de statut

            ev = donne_ev()
            if type_ev(ev) == 'Quitte':
                break
            elif type_ev(ev) == 'ClicGauche':
                x, y = abscisse(ev), ordonnee(ev)
                print(x,y)
                if LARGEUR_FENETRE + 10 <= x <= LARGEUR_TOTALE - 10 and \
                   HAUTEUR_FENETRE // 2 - 25 <= y <= HAUTEUR_FENETRE // 2 + 25:
                    print("Bouton 'Ajout Décors' cliqué !")
                else:
                    self.gerer_clic(x, y, 1)
            elif type_ev(ev) == 'ClicDroit':
                self.gerer_clic(abscisse(ev), ordonnee(ev), 3)
            elif type_ev(ev) == 'Touche':
                t = touche(ev)
                if t == 'a':
                    if self.remplir_auto():
                        print("Carte remplie correctement !")
                        self.afficher_message_status("Carte remplie \n correctement !", duree=200, couleur="green")
                    else:
                        print("Pas moyen de remplir la carte :(")
                        self.afficher_message_status("Pas moyen de \n remplir la carte :(", duree=200, couleur="red")
                elif t == 'c':
                    # Réinitialiser la grille
                    self.grille = [[None for _ in range(NB_CASES)] for _ in range(NB_CASES)]
                    # Réinitialiser le message de statut
                    self.message_status = ""
                    self.timer_status = 0

            mise_a_jour()

        ferme_fenetre()


if __name__ == "__main__":
    app = MapMaker()
    app.setMenu()
