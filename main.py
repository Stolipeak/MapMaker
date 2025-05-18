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
    Voici la classe principale de notre code. Pour simplifier la gestion des infos, le POO semble un meilleur choix
    """

    def __init__(self):

        #Initialisation Variables Du moteur
        self.grille = [[None for _ in range(NB_CASES)] for _ in range(NB_CASES)]
        self.tuiles = self.chargerTuiles("tuiles")
        self.selection = None
        self.menuVisible = False
        self.position_menu = (0, 0)
        self.choixPossibles = []
        self.caseChoisie = None

        #Initialisation Variables Menu : messages
        self.messageStatus = ""
        self.timerStatus = 0
        self.couleurStatus = "green"
        self.menu = "acc"
        
        #Initialisation
        self.decors = []
        self.modeAjoutDecor = False
        self.decos_menuVisible = False
        self.decos_menu_info = None
        self.indicePagination = 0
        self.nbPages = 0
        self.deco_indicePagination = 0
        self.deco_nbPages = 0
        self.origin_x = 0
        self.origin_y = 0
        self.memo_grille = {}
        self.memo_decors = {}
        self.menu_sauvegarde = False


###########################################################################
###    Moteur Graphique : gestion de la coherence de placement de tuiles###
###########################################################################


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


##############################################################################################
###    Interface Graphique : Menu de Lancement. Dessins des tuiles et du menu graphique    ### 
##############################################################################################   


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

    def afficherMessageStatus(self, message, duree=100, couleur="green"):
        """
        Affiche un message de statut dans la barre latérale
        :param message: le message (str)
        :param duree: la durée (int)
        :param couleur: la couleur (en str)
        :return:
        """
        self.messageStatus = message
        self.timerStatus = duree
        self.couleurStatus = couleur

    def dessinerMessageStatus(self):
        """
        Dessine le message de statut dans la barre latérale
        :return:
        """
        texte((LARGEUR_FENETRE + LARGEUR_TOTALE) // 2, 110, "Message Système",
              couleur='black', taille=14, ancrage='center', police='bold')
        rectangle(LARGEUR_FENETRE + 10, 140, LARGEUR_TOTALE - 10, 210, couleur='black', remplissage='white',
                  epaisseur=2)
        if self.timerStatus > 0:
            texte((LARGEUR_FENETRE + LARGEUR_TOTALE) // 2, 175, self.messageStatus,
                  couleur=self.couleurStatus, taille=16, ancrage='center', police='bold')
            self.timerStatus -= 1

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
            if nom_tuile and "S" in nom_tuile:
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
                  couleur='black', remplissage='light blue' if self.modeAjoutDecor else 'white', epaisseur=2)
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
        :param x: abscisse de la case
        :param y: ordonnée de la case
        :param bouton:
        :return:
        """
        self.choixPossibles = self.tuilesPossibles(x, y)
        self.caseChoisie = (x, y)
        self.indicePagination = 0
        self.nbPages = (len(self.choixPossibles) + 4) // 5  # +4 car on garantit un reste pour garantir une dernière page non remplie
        self.menuVisible = True
        if len(self.choixPossibles) > 0:
            self.afficherMessageStatus(f"Tuiles possibles : \n {len(self.choixPossibles)}", duree=200, couleur="green")
        else:
            self.afficherMessageStatus("Aucune tuile \n possible", duree=200, couleur="red")

    def gerer_clic(self, x, y, bouton):
        """
        Gère les clics de la souris sur l'écran de MapMaker
        :param x: abscisse du clic
        :param y: ordonnée du clic
        :param bouton: quel clique ? (int)
        :return:
        """
        # Zone de la grille
        if x < LARGEUR_FENETRE: # Si le clic est dans la zone de la grille
            i, j = y // TAILLE_CASE, x // TAILLE_CASE
            if 0 <= i < NB_CASES and 0 <= j < NB_CASES:
                if self.modeAjoutDecor and self.grille[i][j]:
                    nom_tuile = self.grille[i][j]
                    biomes = set(nom_tuile)
                    biomes_dispo = [b for b in biomes if b in DECORS_PAR_BIOME]
                    if biomes_dispo:
                        biome = biomes_dispo[0]
                        relx = random.randint(16, TAILLE_CASE - 16) # Entre 16 et 48 => 1/4 et 3/4
                        rely = random.randint(16, TAILLE_CASE - 16)
                        self.decos_menu_info = (i, j, biome, relx, rely)
                        self.indicePagination = 0
                        self.menuVisible = True
                    else:
                        self.afficherMessageStatus("Aucun décor \n pour ce biome", couleur="red")
                elif bouton == 1 and not self.modeAjoutDecor:
                    self.menuVisible = True
                    self.choixPossibles = self.tuilesPossibles(i, j)
                    self.caseChoisie = (i, j)
                    self.indicePagination = 0
                    if len(self.choixPossibles) > 0:
                        self.afficherMessageStatus(f"Tuiles possibles : \n {len(self.choixPossibles)}", couleur="green")
                    else:
                        self.afficherMessageStatus("Aucune tuile \n possible", couleur="red")
                elif bouton == 3:
                    self.retirer(i, j)
                    self.menuVisible = False
                    self.decos_menu_info = None
            return

        # Zone du menu latéral
        if LARGEUR_FENETRE <= x <= LARGEUR_TOTALE:
            # Logo MapMaker
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
                    self.menuVisible = True
                    self.menu_sauvegarde = True
                    return

                # Bouton ajout décors
                if HAUTEUR_FENETRE // 2 - 25 <= y <= HAUTEUR_FENETRE // 2 + 25:
                    self.modeAjoutDecor = not self.modeAjoutDecor
                    if self.modeAjoutDecor:
                        self.afficherMessageStatus("Mode Ajout Décor", couleur="blue")
                    else:
                        self.afficherMessageStatus("Mode normal", couleur="green")
                        self.menuVisible = False
                        self.decos_menu_info = None
                    return

            # Menu sauvegarde (en popup)
            if self.menuVisible and self.menu_sauvegarde and 670 <= x <= 810:
                if 420 <= y <= 460:
                    self.sauvegarde()
                    return
                elif 480 <= y <= 520:
                    self.exportPNG()
                elif 540 <= y <= 580:
                    self.menuVisible = False
                    self.menu_sauvegarde = False
                return

            # Flèches menu décors (popup)
            if self.menuVisible and self.nbPages > 1 and 605 <= y <= 625:
                page_actuelle = self.indicePagination // 5
                if 660 <= x <= 710 and page_actuelle > 0: # Flèche gauche
                    self.indicePagination = max(0, self.indicePagination - 5)
                    return
                elif 770 <= x <= 820 and page_actuelle < self.nbPages - 1: # Flèche droite
                    indiceMax = len(self.choixPossibles if not self.modeAjoutDecor else DECORS_PAR_BIOME[
                        self.decos_menu_info[2]]) - 1
                    self.indicePagination = min(self.indicePagination + 5, indiceMax)
                    return

            # Sélection menu popup
            if self.menuVisible and 650 <= x <= 830:
                page_actuelle = self.indicePagination // 5
                debut = page_actuelle * 5
                for idx in range(5):
                    y_pos = 360 + (idx * 45) # Position de l'elem
                    if y_pos <= y <= y_pos + 45:
                        position = debut + idx # Pos dans la liste

                        if self.modeAjoutDecor and self.decos_menu_info: # Menu Decor
                            i, j, biome, relx, rely = self.decos_menu_info
                            decors = DECORS_PAR_BIOME[biome]
                            if position < len(decors): # On a cliqué sur un décor (et pas sur du vide...)
                                self.decors.append((i, j, relx, rely, decors[position]))
                                self.afficherMessageStatus(f"Décor '{decors[position]}' ajouté", couleur="green")
                                self.menuVisible = False
                                self.decos_menu_info = None

                        elif not self.modeAjoutDecor and position < len(self.choixPossibles): # Menu Tuiles
                            iT, jT = self.caseChoisie
                            self.poser(iT, jT, self.choixPossibles[position])
                            self.menuVisible = False
                        return

    def dessiner_menu(self):
        """
        Dessine le menu popup pour les décors et les tuiles (en bien gars)
        :return:
        """
        if not self.menuVisible:
            return # On n'affiche rien si on ne doit pas afficher le menu (logique)

        # Encadré
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
        if self.modeAjoutDecor and self.decos_menu_info:
            i, j, biome, a, b = self.decos_menu_info
            decors = DECORS_PAR_BIOME[biome]
            page_actuelle = self.indicePagination // 5
            debut = page_actuelle * 5
            fin = min(debut + 5, len(decors))
            self.nbPages = (len(decors) + 4) // 5

            if self.nbPages > 1:
                texte(740, 352, f"Page {page_actuelle + 1}/{self.nbPages}",
                      couleur='black', taille=10, ancrage='center')

            for idx, position in enumerate(range(debut, fin)): # Affiche les décors (5 par 5)
                if position < len(decors):
                    decor = decors[position]
                    yCase = 360 + (idx * 45)
                    yCentre = yCase + 22.5
                    rectangle(650, yCase, 830, yCase + 45, couleur="black", epaisseur=1)
                    texte(665, yCentre, decor.capitalize(), couleur='black', taille=10, ancrage='w')
                    if biome == "S":
                        chemin = f"decors/mer/{decor}.png"
                    else:
                        chemin = f"decors/terre/{decor}.png"
                    image(795, yCentre, chemin, largeur=32, hauteur=32, ancrage='center')

        # Sinon on affiche le menu des tuiles
        elif self.choixPossibles:
            page_actuelle = self.indicePagination // 5
            debut = page_actuelle * 5
            fin = min(debut + 5, len(self.choixPossibles))
            self.nbPages = (len(self.choixPossibles) + 4) // 5

            if self.nbPages > 1:
                texte(740, 352, f"Page {page_actuelle + 1}/{self.nbPages}",
                      couleur='black', taille=10, ancrage='center')

            for idx, position in enumerate(range(debut, fin)): # Dessine
                if position < len(self.choixPossibles):
                    code_tuile = self.choixPossibles[position]
                    yCase = 360 + (idx * 45) # Pos verticale de la case
                    yCentre = yCase + 22.5 # 22.5 = la moitié de 45
                    rectangle(650, yCase, 830, yCase + 45, couleur="black", epaisseur=1)
                    texte(665, yCentre, code_tuile, couleur='black', taille=10, ancrage='w')
                    if code_tuile in self.tuiles:
                        image(795, yCentre, self.tuiles[code_tuile],
                              largeur=35, hauteur=35, ancrage='center')

        # Flèches de navigation
        if self.nbPages > 1:
            if page_actuelle > 0: # Flèche gauche
                rectangle(660, 605, 710, 625, couleur="black", remplissage="lightgray")
                polygone([(670, 615), (680, 605), (680, 625)], couleur="black", remplissage="black")
            if page_actuelle < self.nbPages - 1: # Flèche droite
                rectangle(770, 605, 820, 625, couleur="black", remplissage="lightgray")
                polygone([(810, 615), (800, 605), (800, 625)], couleur="black", remplissage="black")



###############################################################################################
###   Solveur MapMaker amelioré avec optimisations et limitation pour eviter les crash      ###
###############################################################################################



    def solveur(self):
    # Crée une liste des cases vides avec le nombre de contraintes (voisins non vides)
        cases_vides = []
        for i in range(NB_CASES):
            for j in range(NB_CASES):
                if self.grille[i][j] is None:
                    # Compter les voisins non vides
                    contraintes = 0
                    if i > 0 and self.grille[i-1][j] is not None: contraintes += 1
                    if j > 0 and self.grille[i][j-1] is not None: contraintes += 1
                    if i < NB_CASES-1 and self.grille[i+1][j] is not None: contraintes += 1
                    if j < NB_CASES-1 and self.grille[i][j+1] is not None: contraintes += 1
                    cases_vides.append((contraintes, i, j))
        
        # Trie les cases par nombre de contraintes décroissant (cases les plus contraintes en premier)
        cases_vides.sort(reverse=True, key=lambda x: x[0])
        if not cases_vides:
            return True
        
        _, i, j = cases_vides[0]
        tuiles_valides = self.tuilesPossibles(i, j)
        if not tuiles_valides:
            return False
        
        random.shuffle(tuiles_valides)
        max_tentatives = min(10, len(tuiles_valides))
        for tuile in tuiles_valides[:max_tentatives]:
            self.grille[i][j] = tuile
            if self.solveur():
                return True
            self.grille[i][j] = None
        
        return False



###############################################################################
###     Sauvegarde : Chargements des anciennes maps et Exportation en png   ###
###############################################################################


    def sauvegarde(self):
        """
        Sauvegarde la carte dans un fichier .sav
        :return: .sav
        """
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

        self.afficherMessageStatus(f"Carte sauvegardée : \n {fichier}", couleur="green")
        self.menuVisible = False
        self.menu_sauvegarde = False

    def charger(self):
        """
        Charge une carte à partir d'un fichier .sav
        :return:
        """
        if not os.path.exists("saves"):
            os.makedirs("saves")

        root = Tk() # Ouvre une page (qu'on va cacher direct)
        root.withdraw() #Cache la fenetre root

        fichier = filedialog.askopenfilename(
            initialdir="saves", # Dossier par défaut
            title="Sélectionner une map à charger", # Titre de la fenêtre
            filetypes=(("Fichiers de sauvegarde", "*.sav"), ("Tous les fichiers", "*.*"))
        )



        with open(fichier, 'r') as f:
            lignes = f.readlines()
            for ligne in lignes:
                elements = ligne.strip().split(';') # [TUILE, i, j, code]
                if elements[0] == "TUILE":
                    i, j, tuile = int(elements[1]), int(elements[2]), elements[3]
                    self.grille[i][j] = tuile
                elif elements[0] == "DECOR":
                    i, j, relx, rely, type_decor = int(elements[1]), int(elements[2]), int(elements[3]), int(
                        elements[4]), elements[5]
                    self.decors.append((i, j, relx, rely, type_decor))

    def exportPNG(self):
        """
        Exporte la carte au format png
        :return: .png
        """
        tailleTotale = NB_CASES * TAILLE_CASE
        carteImg = Image.new("RGBA", (tailleTotale, tailleTotale), (200, 200, 200, 255)) # Couleur de fond (gris clair

        # Dessiner les tuiles
        for i in range(NB_CASES):
            for j in range(NB_CASES):
                if self.grille[i][j] is not None:
                    cheminTuile = self.tuiles[self.grille[i][j]]
                    tuileImg = Image.open(cheminTuile).convert("RGBA") # Ouvrir l'image
                    tuileImg = tuileImg.resize((TAILLE_CASE, TAILLE_CASE)) # Redimensionner l'image
                    carteImg.paste(tuileImg, (j * TAILLE_CASE, i * TAILLE_CASE)) # Ajoute l'image à la carte

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
                x = j * TAILLE_CASE + relx - 16 # Décalage pour centrer le décor
                y = i * TAILLE_CASE + rely - 16

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
        self.afficherMessageStatus(f"Carte exportée : \n {cheminExport}", couleur="green")
        self.menuVisible = False
        self.menu_sauvegarde = False
        return True


#################################################################################
###    Boucle de lancement du jeu et gestion des clique clavier et souris     ###
#################################################################################


    def boucle_principale(self):
        while True:
            efface_tout()
            self.dessiner()
            self.dessiner_menu()
            self.dessinerMessageStatus()

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
                        self.afficherMessageStatus("Carte remplie correctement !", duree=200, couleur="green")
                    else:
                        self.afficherMessageStatus("Pas moyen de remplir la carte :(", duree=200, couleur="red")
                elif t == 'c':
                    self.grille = [[None for _ in range(NB_CASES)] for _ in range(NB_CASES)]
                    self.decors = []
                    self.messageStatus = ""
                    self.timerStatus = 0
            mise_a_jour()
        ferme_fenetre()


if __name__ == "__main__":
    app = MapMaker()
    app.setMenu()
