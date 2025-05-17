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
        self.menu_visible = False
        self.position_menu = (0, 0)
        self.choix_possibles = []
        self.case_choisie = None
        self.message_status = ""  # Message de statut
        self.timer_status = 0  # Compteur pour le message
        self.couleur_status = "green"  # Couleur par défaut du message
        self.menu = "acc"

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

    def tuiles_possibles(self, i, j):
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
        essais = self.tuiles_possibles(i, j)

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
        rectangle(650, 360, 830, 630, couleur="black", remplissage='white', epaisseur=2)
        # Lignes horizontales pour diviser en 6 rangées
        ligne(650, 405, 830, 405, couleur="black", epaisseur=1)  # 1ère ligne horizontale
        ligne(650, 450, 830, 450, couleur="black", epaisseur=1)  # 2ème ligne horizontale
        ligne(650, 495, 830, 495, couleur="black", epaisseur=1)  # 3ème ligne horizontale
        ligne(650, 540, 830, 540, couleur="black", epaisseur=1)  # 4ème ligne horizontale
        ligne(650, 585, 830, 585, couleur="black", epaisseur=1)  # 5ème ligne horizontale


    def dessiner_menu(self):
        # montre les choix de tuiles si besoin
        if not self.menu_visible:
            return

        x, y = self.position_menu






        """largeur = 180
        for idx, t in enumerate(self.choix_possibles[:10]):
            yopt = y + 10 + idx * 30
            rectangle(x + 5, yopt - 5, x + largeur - 5, yopt + 25, couleur='black', remplissage='white', epaisseur=2)
            texte(x + 10, yopt, t, couleur='black', taille=12)
            if t in self.tuiles:
                try:
                    image(x + largeur - 30, yopt + 10, self.tuiles[t], largeur=30, hauteur=30, ancrage='center')
                except:
                    pass"""

    def gerer_clic(self, x, y, bouton):
        # clic gauche ou droit sur la grille
        i, j = y // TAILLE_CASE, x // TAILLE_CASE

        if 0 <= i < NB_CASES and 0 <= j < NB_CASES:
            if bouton == 1:
                if self.menu_visible:
                    mx, my = self.position_menu
                    if mx <= x <= mx + 180 and my <= y <= my + 300:
                        choix = (y - my - 10) // 30
                        if 0 <= choix < len(self.choix_possibles):
                            if self.case_choisie:
                                ci, cj = self.case_choisie
                                self.poser(ci, cj, self.choix_possibles[choix])
                    self.menu_visible = False
                    self.case_choisie = None
                else:
                    self.case_choisie = (i, j)
                    self.choix_possibles = self.tuiles_possibles(i, j)
                    if self.choix_possibles:
                        self.menu_visible = True
                        self.position_menu = (x, y)
                    else:
                        print("Pas de tuiles compatibles ici...")
            elif bouton == 3:
                self.retirer(i, j)
                self.menu_visible = False
                self.case_choisie = None

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
