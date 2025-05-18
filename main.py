from fltk import *
import os
import random
import winsound
from tkinter import Tk
from tkinter import filedialog
from PIL import Image

# paramètres de base
TAILLE_CASE = 64
NB_CASES = 10
LARGEUR_FENETRE = NB_CASES * TAILLE_CASE
HAUTEUR_FENETRE = NB_CASES * TAILLE_CASE
LARGEUR_BARRE = 200
LARGEUR_TOTALE = LARGEUR_FENETRE + LARGEUR_BARRE

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

DECORS_PAR_BIOME = {
    'S': ["serpent", "ship", "siren", "wave", "wave2"],
    'P': ["black_city", "city", "field", "grass", "grass2", "sheep", "village"]
}


class MapMaker:
    """
    Classe principale pour le MapMaker.
    """
    def __init__(self):
        self.grille = [[None for _ in range(NB_CASES)] for _ in range(NB_CASES)]
        self.tuiles = self.chargerTuiles("tuiles")
        self.selection = None
        self.menu_visible = False
        self.position_menu = (0, 0)
        self.choixPossibles = []
        self.caseChoisie = None
        self.message_status = ""
        self.timer_status = 0
        self.couleur_status = "green"
        self.menu = "acc"
        self.decors = []
        self.mode_ajout_decor = False
        self.decos_menu_visible = False
        self.decos_menu_info = None
        self.indice = 0
        self.nbPages = 0
        self.deco_indice = 0
        self.deco_nbPages = 0
        self.origin_x = 0
        self.origin_y = 0
        self.memo_grille = {}
        self.memo_decors = {}
        self.menu_sauvegarde = False

    def setMenu(self):
        """
        Fonction pour afficher le menu d'accueil ou le menu de MapMaker

        :return:
        """
        if self.menu == "acc":
            cree_fenetre(600, 600)
            efface_tout()
            winsound.PlaySound("media/nouveauTheme.wav", winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)
            rectangle(0, 0, 600, 600, couleur='sky blue', remplissage='sky blue')
            cloud_positions = [ # Positions des nuages pour l'arrière-plan
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
            for x, y in cloud_positions:
                image(x, y, "media/cloud.png", largeur=80, hauteur=80, ancrage='nw')

            # Logo MapMaker
            image(300, 100, "media/logoMM.png", largeur=300, hauteur=300, ancrage='center')
            # Bouton MapMaker
            rectangle(200, 250, 400, 300, couleur='black', remplissage='white', epaisseur=2)
            texte(300, 275, "MapMaker", couleur='black', taille=16, ancrage='center')
            # Bouton Charger
            rectangle(200, 330, 400, 380, couleur='black', remplissage='white', epaisseur=2)
            texte(300, 355, "Charger", couleur='black', taille=16, ancrage='center')
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
                    if 200 <= x <= 400 and 300 >= y >= 250:
                        self.menu = "MapMaker"
                        ferme_fenetre()
                        cree_fenetre(LARGEUR_TOTALE, HAUTEUR_FENETRE)
                        self.boucle_principale()
                        return
                    elif 200 <= x <= 400 and 380 >= y >= 330:
                        self.menu = "MapMaker"
                        self.charger()
                        ferme_fenetre()
                        cree_fenetre(LARGEUR_TOTALE, HAUTEUR_FENETRE)
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
                mise_a_jour()
            ferme_fenetre()


    def chargerTuiles(self, dossier):
        """
        Charge les tuiles à partir du dossier /tuiles
        :param dossier: /tuiles
        :return: dictionnaire des tuiles
        """
        tuiles = {}
        if os.path.exists(dossier):
            for fichier in os.listdir(dossier):
                if fichier.endswith(".png"):
                    nom = fichier.split(".")[0]
                    if len(nom) == 4:
                        tuiles[nom] = os.path.join(dossier, fichier)
        return tuiles

    def caseOk(self, i, j, code):
        """
        Vérifie si on peut poser la case à l'endroit (i,j)
        :param i: l'abscisse de la case
        :param j: l'ordonnée de la case
        :param code: le nom de la tuile
        :return: True or False si on peut poser la case ou pas
        """
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
        """
        Renvoie la liste des tuiles possibles à poser sur la case (i,j)
        :param i: abscisse de la case
        :param j: ordonnée de la case
        :return: liste des tuiles possibles
        """
        possibles = []
        for t in self.tuiles:
            if self.caseOk(i, j, t):
                possibles.append(t)
        return possibles

    def poser(self, i, j, code):
        """
        Pose la tuile code à la case (i,j) si c'est possible
        :param i: abscisse de la case
        :param j: ordonnée de la case
        :param code: nom de la case
        :return:
        """
        if self.caseOk(i, j, code):
            self.grille[i][j] = code
            return True
        return False

    def retirer(self, i, j):
        """
        Retire la tuile de la case (i,j)
        :param i: abscisse de la case
        :param j: ordonnée de la case
        :return:
        """
        self.grille[i][j] = None
        self.decors = [d for d in self.decors if not (d[0] == i and d[1] == j)]

    def solveur(self):
        """
        Génère une carte aléatoire
        :return: 
        """
        cases_vides = [(ligne, col) for ligne in range(NB_CASES) for col in range(NB_CASES) if
                       self.grille[ligne][col] is None]
        if not cases_vides:
            return True
        ligne, col = cases_vides[0]

        # On récupère toutes les tuiles valides pour cette case
        tuiles_valides = self.tuilesPossibles(ligne, col)
        # Mélange aléatoire pour casser les patterns répétitifs
        random.shuffle(tuiles_valides)
        # Tri pour éviter les tuiles identiques côte à côte (plus esthétique)
        voisins = []
        if ligne > 0 and self.grille[ligne - 1][col]: voisins.append(self.grille[ligne - 1][col])
        if col > 0 and self.grille[ligne][col - 1]: voisins.append(self.grille[ligne][col - 1])
        tuiles_ordonnee = sorted(tuiles_valides, key=lambda tuile: sum(1 for v in voisins if v == tuile))

        for tuile in tuiles_ordonnee:
            self.grille[ligne][col] = tuile
            if self.solveur():
                return True
            self.grille[ligne][col] = None
        return False

    def afficher_message_status(self, message, duree=100, couleur="green"):
        """
        Affiche un message de statut dans la barre latérale
        :param message: le message (str)
        :param duree: la durée (int)
        :param couleur: la couleur (en str)
        :return: 
        """
        self.message_status = message
        self.timer_status = duree
        self.couleur_status = couleur

    def dessiner_message_status(self):
        """
        Dessine le message de statut dans la barre latérale
        :return: 
        """
        texte((LARGEUR_FENETRE + LARGEUR_TOTALE) // 2, 110, "Message Système",
              couleur='black', taille=14, ancrage='center', police='bold')
        rectangle(LARGEUR_FENETRE + 10, 140, LARGEUR_TOTALE - 10, 210, couleur='black', remplissage='white',
                  epaisseur=2)
        if self.timer_status > 0:
            texte((LARGEUR_FENETRE + LARGEUR_TOTALE) // 2, 175, self.message_status,
                  couleur=self.couleur_status, taille=16, ancrage='center', police='bold')
            self.timer_status -= 1

    def dessiner(self):
        """
        Dessine la grille et les tuiles
        :return: 
        """
        # Grille + tuiles
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

        # Décors posés
        for decor in self.decors:
            i, j, relx, rely, type_decor = decor
            nom_tuile = self.grille[i][j]
            if type_decor in DECORS_PAR_BIOME.get('S', []):
                chemin = f"decors/mer/{type_decor}.png"
            else:
                chemin = f"decors/terre/{type_decor}.png"
            x = j * TAILLE_CASE + relx
            y = i * TAILLE_CASE + rely
            image(x, y, chemin, largeur=32, hauteur=32, ancrage='center')

        # Barre latérale
        rectangle(LARGEUR_FENETRE, 0, LARGEUR_TOTALE, HAUTEUR_FENETRE, couleur='black', remplissage='white')
        image((LARGEUR_FENETRE + LARGEUR_TOTALE) // 2, 50, "media/logoMM.png", largeur=120, hauteur=120,
              ancrage='center')

        # Bouton Ajout Décors
        rectangle(LARGEUR_FENETRE + 10, HAUTEUR_FENETRE // 2 - 25, LARGEUR_TOTALE - 10, HAUTEUR_FENETRE // 2 + 25,
                  couleur='black', remplissage='light blue' if self.mode_ajout_decor else 'white', epaisseur=2)
        texte((LARGEUR_FENETRE + LARGEUR_TOTALE) // 2, HAUTEUR_FENETRE // 2, "Ajout Décors",
              couleur='black', taille=16, ancrage='center')

        # Bouton de sauvegarde
        rectangle(LARGEUR_FENETRE + 10, HAUTEUR_FENETRE // 2 - 100, LARGEUR_TOTALE - 10, HAUTEUR_FENETRE // 2 - 50,
                  couleur='black', remplissage='white', epaisseur=2)
        texte((LARGEUR_FENETRE + LARGEUR_TOTALE) // 2, HAUTEUR_FENETRE // 2 - 75, "Sauvegarder",
              couleur='black', taille=16, ancrage='center')




    def afficheTuilesPossibles(self, x, y, bouton):
        """
        Affiche les tuiles possibles à poser sur la case (x,y)
        :param x: 
        :param y: 
        :param bouton: 
        :return: 
        """
        self.choixPossibles = self.tuilesPossibles(x, y)
        self.caseChoisie = (x, y)
        self.indice = 0
        self.nbPages = (len(self.choixPossibles) + 4) // 5  # +4 car on garantit un reste pour garantir une dernière page non remplie
        self.menu_visible = True
        if len(self.choixPossibles) > 0:
            self.afficher_message_status(f"Tuiles possibles : \n {len(self.choixPossibles)}", duree=200, couleur="green")
        else:
            self.afficher_message_status("Aucune tuile \n possible", duree=200, couleur="red")

    def gerer_clic(self, x, y, bouton):
        """
        Gère les clics de la souris sur MapMaker
        :param x: abscisse du clic
        :param y: ordonnée du clic
        :param bouton: touche du clavier
        :return: 
        """
        # Zone de la grille
        if x < LARGEUR_FENETRE:
            i, j = y // TAILLE_CASE, x // TAILLE_CASE
            if 0 <= i < NB_CASES and 0 <= j < NB_CASES:
                if self.mode_ajout_decor and self.grille[i][j]:
                    nom_tuile = self.grille[i][j]
                    biomes = set(nom_tuile)
                    biomes_dispo = [b for b in biomes if b in DECORS_PAR_BIOME]
                    if biomes_dispo:
                        biome = biomes_dispo[0]
                        relx = random.randint(16, TAILLE_CASE - 16)
                        rely = random.randint(16, TAILLE_CASE - 16)
                        self.decos_menu_info = (i, j, biome, relx, rely)
                        self.indice = 0
                        self.menu_visible = True
                    else:
                        self.afficher_message_status("Aucun décor pour ce biome", couleur="red")
                elif bouton == 1 and not self.mode_ajout_decor:
                    self.menu_visible = True
                    self.choixPossibles = self.tuilesPossibles(i, j)
                    self.caseChoisie = (i, j)
                    self.indice = 0
                    if len(self.choixPossibles) > 0:
                        self.afficher_message_status(f"Tuiles possibles : {len(self.choixPossibles)}", couleur="green")
                    else:
                        self.afficher_message_status("Aucune tuile possible", couleur="red")
                elif bouton == 3:
                    self.retirer(i, j)
                    self.menu_visible = False
                    self.decos_menu_info = None
            return

        # Zone du menu latéral
        if LARGEUR_FENETRE <= x <= LARGEUR_TOTALE:
            # Logo MapMaker (en haut)
            logo_centre_x = (LARGEUR_FENETRE + LARGEUR_TOTALE) // 2
            logo_centre_y = 50
            if (logo_centre_x - 60 <= x <= logo_centre_x + 60) and (logo_centre_y - 60 <= y <= logo_centre_y + 60):
                self.menu = "acc"
                ferme_fenetre()
                self.setMenu()
                return

            # Zone des boutons
            if LARGEUR_FENETRE + 10 <= x <= LARGEUR_TOTALE - 10:
                # Bouton sauvegarde
                if HAUTEUR_FENETRE // 2 - 100 <= y <= HAUTEUR_FENETRE // 2 - 50:
                    self.menu_visible = True
                    self.menu_sauvegarde = True
                    return

                # Bouton ajout décors
                if HAUTEUR_FENETRE // 2 - 25 <= y <= HAUTEUR_FENETRE // 2 + 25:
                    self.mode_ajout_decor = not self.mode_ajout_decor
                    if self.mode_ajout_decor:
                        self.afficher_message_status("Mode Ajout Décor", couleur="blue")
                    else:
                        self.afficher_message_status("Mode normal", couleur="green")
                        self.menu_visible = False
                        self.decos_menu_info = None
                    return

            # Menu popup de sauvegarde
            if self.menu_visible and self.menu_sauvegarde and 670 <= x <= 810:
                if 420 <= y <= 460:
                    self.sauvegarde()
                    return
                elif 480 <= y <= 520:
                    self.exportPNG()
                elif 540 <= y <= 580:
                    self.menu_visible = False
                    self.menu_sauvegarde = False
                return

            # Navigation dans le menu de sélection
            if self.menu_visible and self.nbPages > 1 and 605 <= y <= 625:
                page_actuelle = self.indice // 5
                if 660 <= x <= 710 and page_actuelle > 0:
                    self.indice = max(0, self.indice - 5)
                    return
                elif 770 <= x <= 820 and page_actuelle < self.nbPages - 1:
                    max_index = len(self.choixPossibles if not self.mode_ajout_decor else DECORS_PAR_BIOME[
                        self.decos_menu_info[2]]) - 1
                    self.indice = min(self.indice + 5, max_index)
                    return

            # Sélection dans le menu
            if self.menu_visible and 650 <= x <= 830:
                page_actuelle = self.indice // 5
                debut = page_actuelle * 5
                for idx in range(5):
                    y_pos = 360 + (idx * 45)
                    if y_pos <= y <= y_pos + 45:
                        position = debut + idx
                        if self.mode_ajout_decor and self.decos_menu_info:
                            i, j, biome, relx, rely = self.decos_menu_info
                            decors = DECORS_PAR_BIOME[biome]
                            if position < len(decors):
                                self.decors.append((i, j, relx, rely, decors[position]))
                                self.afficher_message_status(f"Décor '{decors[position]}' ajouté", couleur="green")
                                self.menu_visible = False
                                self.decos_menu_info = None
                        elif not self.mode_ajout_decor and position < len(self.choixPossibles):
                            ci, cj = self.caseChoisie
                            self.poser(ci, cj, self.choixPossibles[position])
                            self.menu_visible = False
                        return

    def dessiner_menu(self):
        if not self.menu_visible:
            return

        # Grand rectangle principal
        rectangle(650, 360, 830, 585, couleur="black", remplissage='white', epaisseur=2)

        # Menu de sauvegarde
        if self.menu_sauvegarde:
            texte(740, 380, "Confirmer la sauvegarde ?", couleur='black', taille=12, ancrage='center')
            rectangle(670, 420, 810, 460, couleur="black", remplissage='lightgreen', epaisseur=2)
            texte(740, 440, "Sauvegarder .sav", couleur='black', taille=12, ancrage='center')
            rectangle(670, 480, 810, 520, couleur="black", remplissage='lightblue', epaisseur=2)
            texte(740, 500, "Sauvegarder .png", couleur='black', taille=12, ancrage='center')
            rectangle(670, 540, 810, 580, couleur="black", remplissage='lightgray', epaisseur=2)
            texte(740, 560, "Annuler", couleur='black', taille=12, ancrage='center')

            return

        # En mode ajout décor, on affiche le menu des décors
        if self.mode_ajout_decor and self.decos_menu_info:
            i, j, biome, relx, rely = self.decos_menu_info
            decors = DECORS_PAR_BIOME[biome]
            page_actuelle = self.indice // 5
            debut = page_actuelle * 5
            fin = min(debut + 5, len(decors))
            self.nbPages = (len(decors) + 4) // 5

            if self.nbPages > 1:
                texte(740, 352, f"Page {page_actuelle + 1}/{self.nbPages}",
                      couleur='black', taille=10, ancrage='center')

            for idx, position in enumerate(range(debut, fin)):
                if position < len(decors):
                    decor = decors[position]
                    y_base = 360 + (idx * 45)
                    y_centre = y_base + 22.5
                    rectangle(650, y_base, 830, y_base + 45, couleur="black", epaisseur=1)
                    texte(665, y_centre, decor.capitalize(), couleur='black', taille=10, ancrage='w')
                    if biome == "S":
                        chemin = f"decors/mer/{decor}.png"
                    else:
                        chemin = f"decors/terre/{decor}.png"
                    image(795, y_centre, chemin, largeur=32, hauteur=32, ancrage='center')

        # Sinon on affiche le menu des tuiles
        elif self.choixPossibles:
            page_actuelle = self.indice // 5
            debut = page_actuelle * 5
            fin = min(debut + 5, len(self.choixPossibles))
            self.nbPages = (len(self.choixPossibles) + 4) // 5

            if self.nbPages > 1:
                texte(740, 352, f"Page {page_actuelle + 1}/{self.nbPages}",
                      couleur='black', taille=10, ancrage='center')

            for idx, position in enumerate(range(debut, fin)):
                if position < len(self.choixPossibles):
                    code_tuile = self.choixPossibles[position]
                    y_base = 360 + (idx * 45)
                    y_centre = y_base + 22.5
                    rectangle(650, y_base, 830, y_base + 45, couleur="black", epaisseur=1)
                    texte(665, y_centre, code_tuile, couleur='black', taille=10, ancrage='w')
                    if code_tuile in self.tuiles:
                        image(795, y_centre, self.tuiles[code_tuile],
                              largeur=35, hauteur=35, ancrage='center')

        # Flèches de navigation
        if self.nbPages > 1:
            if page_actuelle > 0:
                rectangle(660, 605, 710, 625, couleur="black", remplissage="lightgray")
                polygone([(670, 615), (680, 605), (680, 625)], couleur="black", remplissage="black")
            if page_actuelle < self.nbPages - 1:
                rectangle(770, 605, 820, 625, couleur="black", remplissage="lightgray")
                polygone([(810, 615), (800, 605), (800, 625)], couleur="black", remplissage="black")

    def sauvegarde(self):
        # Créer le dossier saves s'il n'existe pas
        if not os.path.exists("saves"):
            os.makedirs("saves")

        # Trouver le prochain numéro de sauvegarde disponible
        num = 1
        while os.path.exists(f"saves/carte_{num}.sav"):
            num += 1

        fichier = f"saves/carte_{num}.sav"

        with open(fichier, 'w') as f:
            # Sauvegarde des tuiles
            for i in range(NB_CASES):
                for j in range(NB_CASES):
                    if self.grille[i][j] is not None:
                        f.write(f"TUILE;{i};{j};{self.grille[i][j]}\n")

            # Sauvegarde des décors
            for decor in self.decors:
                i, j, relx, rely, type_decor = decor
                f.write(f"DECOR;{i};{j};{relx};{rely};{type_decor}\n")

        self.afficher_message_status(f"Carte sauvegardée : \n {fichier}", couleur="green")
        self.menu_visible = False
        self.menu_sauvegarde = False

    def charger(self):
        if not os.path.exists("saves"):
            os.makedirs("saves")

        root = Tk()
        root.withdraw() #Cache la fenetre root

        fichier = filedialog.askopenfilename(
            initialdir="saves",
            title="Sélectionner une map à charger",
            filetypes=(("Fichiers de sauvegarde", "*.sav"), ("Tous les fichiers", "*.*"))
        )



        with open(fichier, 'r') as f:
            lignes = f.readlines()
            for ligne in lignes:
                elements = ligne.strip().split(';')
                if elements[0] == "TUILE":
                    i, j, tuile = int(elements[1]), int(elements[2]), elements[3]
                    self.grille[i][j] = tuile
                elif elements[0] == "DECOR":
                    i, j, relx, rely, type_decor = int(elements[1]), int(elements[2]), int(elements[3]), int(
                        elements[4]), elements[5]
                    self.decors.append((i, j, relx, rely, type_decor))


    def exportPNG(self):
        tailleTotale = NB_CASES * TAILLE_CASE
        carteImg = Image.new("RGBA", (tailleTotale, tailleTotale), (200, 200, 200, 255))

        # Dessiner les tuiles
        for i in range(NB_CASES):
            for j in range(NB_CASES):
                if self.grille[i][j] is not None:
                    cheminTuile = self.tuiles[self.grille[i][j]]
                    tuileImg = Image.open(cheminTuile).convert("RGBA")
                    tuileImg = tuileImg.resize((TAILLE_CASE, TAILLE_CASE))
                    carteImg.paste(tuileImg, (j * TAILLE_CASE, i * TAILLE_CASE))

        # Dessiner les décors
        for decor in self.decors:
            i, j, relx, rely, typeDecor = decor
            if "S" in self.grille[i][j]:
                cheminDecor = f"decors/mer/{typeDecor}.png"
            else:
                cheminDecor = f"decors/terre/{typeDecor}.png"

            if os.path.exists(cheminDecor):
                decorImg = Image.open(cheminDecor).convert("RGBA")
                decorImg = decorImg.resize((32, 32))
                x = j * TAILLE_CASE + relx - 16
                y = i * TAILLE_CASE + rely - 16
                # Créer un masque de transparence
                r, g, b, a = decorImg.split()
                carteImg.paste(decorImg, (x, y), mask=a)

        # Créer le dossier export si nécessaire
        if not os.path.exists("export"):
            os.makedirs("export")

        # Trouver le prochain numéro disponible
        num = 1
        while os.path.exists(f"export/carte_{num}.png"):
            num += 1

        cheminExport = f"export/carte_{num}.png"
        carteImg.save(cheminExport)
        self.afficher_message_status(f"Carte exportée : \n {cheminExport}", couleur="green")
        self.menu_visible = False
        self.menu_sauvegarde = False
        return True




    def boucle_principale(self):
        while True:
            efface_tout()
            self.dessiner()
            self.dessiner_menu()
            self.dessiner_message_status()

            ev = donne_ev()
            if type_ev(ev) == 'Quitte':
                break
            elif type_ev(ev) == 'ClicGauche':
                x, y = abscisse(ev), ordonnee(ev)
                self.gerer_clic(x, y, 1)
            elif type_ev(ev) == 'ClicDroit':
                self.gerer_clic(abscisse(ev), ordonnee(ev), 3)
            elif type_ev(ev) == 'Touche':
                t = touche(ev)
                if t == 'a':
                    if self.solveur():
                        self.afficher_message_status("Carte remplie correctement !", duree=200, couleur="green")
                    else:
                        self.afficher_message_status("Pas moyen de remplir la carte :(", duree=200, couleur="red")
                elif t == 'c':
                    self.grille = [[None for _ in range(NB_CASES)] for _ in range(NB_CASES)]
                    self.decors = []
                    self.message_status = ""
                    self.timer_status = 0
            mise_a_jour()
        ferme_fenetre()


if __name__ == "__main__":
    app = MapMaker()
    app.setMenu()