from fltk import *
import os
import random
import winsound

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
    'S': ["serpent", "ship", "siren", "wave","wave2"],
    'P': ["black_city", "city", "field", "grass","grass2", "sheep", "village"]
}

class MapMaker:
    def __init__(self):
        self.grille = [[None for _ in range(NB_CASES)] for _ in range(NB_CASES)]
        self.tuiles = self.charger_tuiles("tuiles")
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
        self.origin_x = 0  # Décalage horizontal (case en haut à gauche affichée)
        self.origin_y = 0  # Décalage vertical
        self.memo_grille = {}   # Dictionnaire {(i, j): code_tuile} pour stocker les cases générées
        self.memo_decors = {}   # Dictionnaire {(i, j): [tuple decors]} pour stocker les décors générés


    def setMenu(self):
        if self.menu == "acc":
            cree_fenetre(600, 600)
            efface_tout()
            winsound.PlaySound("media/nouveauTheme.wav", winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)
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
            for x, y in cloud_positions:
                image(x, y, "media/cloud.png", largeur=80, hauteur=80, ancrage='nw')
            image(300, 100, "media/logoMM.png", largeur=300, hauteur=300, ancrage='center')
            rectangle(200, 290, 400, 340, couleur='black', remplissage='white', epaisseur=2)
            texte(300, 315, "MapMaker", couleur='black', taille=16, ancrage='center')
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
                        self.menu = "MapMaker"
                        ferme_fenetre()
                        cree_fenetre(LARGEUR_TOTALE, HAUTEUR_FENETRE)
                        self.boucle_principale()
                        return
                    elif 550 <= x <= 600 and 52 >= y >= 2:
                        if isSound:
                            isSound = False
                            winsound.PlaySound(None, winsound.SND_ASYNC)
                            efface("isSound")
                            image(575, 27, "media/stopSound.png", largeur=20, hauteur=20, ancrage='center', tag="isSound")
                        else:
                            isSound = True
                            winsound.PlaySound("media/nouveauTheme.wav", winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)
                            efface("isSound")
                            image(575, 27, "media/goSound.png", largeur=20, hauteur=20, ancrage='center', tag="isSound")
                mise_a_jour()
            ferme_fenetre()
        else:
            cree_fenetre(LARGEUR_TOTALE, HAUTEUR_FENETRE)
            self.boucle_principale()

    def charger_tuiles(self, dossier):
        tuiles = {}
        if os.path.exists(dossier):
            for fichier in os.listdir(dossier):
                if fichier.endswith(".png"):
                    nom = fichier.split(".")[0]
                    if len(nom) == 4:
                        tuiles[nom] = os.path.join(dossier, fichier)
        return tuiles

    def case_ok(self, i, j, code):
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
        possibles = []
        for t in self.tuiles:
            if self.case_ok(i, j, t):
                possibles.append(t)
        return possibles

    def poser(self, i, j, code):
        if self.case_ok(i, j, code):
            self.grille[i][j] = code
            return True
        return False

    def retirer(self, i, j):
        self.grille[i][j] = None
        self.decors = [d for d in self.decors if not (d[0] == i and d[1] == j)]

    def generer_carte_aleatoire(self):
        cases_vides = [(ligne, col) for ligne in range(NB_CASES) for col in range(NB_CASES) if self.grille[ligne][col] is None]
        if not cases_vides:
            return True
        ligne, col = cases_vides[0]

        # On récupère toutes les tuiles valides pour cette case
        tuiles_valides = self.tuilesPossibles(ligne, col)
        # Mélange aléatoire pour casser les patterns répétitifs
        random.shuffle(tuiles_valides)
        # Tri pour éviter les tuiles identiques côte à côte (plus esthétique)
        voisins = []
        if ligne > 0 and self.grille[ligne-1][col]: voisins.append(self.grille[ligne-1][col])
        if col > 0 and self.grille[ligne][col-1]: voisins.append(self.grille[ligne][col-1])
        tuiles_ordonnee = sorted(tuiles_valides, key=lambda tuile: sum(1 for v in voisins if v == tuile))

        for tuile in tuiles_ordonnee:
            self.grille[ligne][col] = tuile
            if self.generer_carte_aleatoire():
                return True
            self.grille[ligne][col] = None
        return False

    def afficher_message_status(self, message, duree=100, couleur="green"):
        self.message_status = message
        self.timer_status = duree
        self.couleur_status = couleur

    def dessiner_message_status(self):
        texte((LARGEUR_FENETRE + LARGEUR_TOTALE) // 2, 110, "Message Système",
              couleur='black', taille=14, ancrage='center', police='bold')
        rectangle(LARGEUR_FENETRE + 10, 140, LARGEUR_TOTALE - 10, 210, couleur='black', remplissage='white',
                  epaisseur=2)
        if self.timer_status > 0:
            texte((LARGEUR_FENETRE + LARGEUR_TOTALE) // 2, 175, self.message_status,
                  couleur=self.couleur_status, taille=16, ancrage='center', police='bold')
            self.timer_status -= 1

    def dessiner(self):
        # Grille + tuiles
        for i in range(NB_CASES):
            for j in range(NB_CASES):
                x = j * TAILLE_CASE
                y = i * TAILLE_CASE
                if self.grille[i][j] is not None:
                    chemin = self.tuiles[self.grille[i][j]]
                    image(x, y, chemin, largeur=TAILLE_CASE, hauteur=TAILLE_CASE, ancrage='nw')
                else:
                    rectangle(x, y, x + TAILLE_CASE, y + TAILLE_CASE, couleur='black', remplissage='light gray', epaisseur=1)
        
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
        image((LARGEUR_FENETRE + LARGEUR_TOTALE) // 2, 50, "media/logoMM.png", largeur=120, hauteur=120, ancrage='center')
        
        # Bouton Ajout Décors
        rectangle(LARGEUR_FENETRE + 10, HAUTEUR_FENETRE // 2 - 25, LARGEUR_TOTALE - 10, HAUTEUR_FENETRE // 2 + 25,
                couleur='black', remplissage='light blue' if self.mode_ajout_decor else 'white', epaisseur=2)
        texte((LARGEUR_FENETRE + LARGEUR_TOTALE) // 2, HAUTEUR_FENETRE // 2, "Ajout Décors",
            couleur='black', taille=16, ancrage='center')
            
        # Menu décor si visible
        if self.decos_menu_visible and self.decos_menu_info:
            self.dessiner_menu_decor()

    def dessiner_menu_decor(self):
        i, j, biome, relx, rely = self.decos_menu_info
        decors = DECORS_PAR_BIOME[biome]
        n_par_page = 5
        nbPages = (len(decors) + n_par_page - 1) // n_par_page
        page_actuelle = self.deco_indice // n_par_page
        debut = page_actuelle * n_par_page
        fin = min(debut + n_par_page, len(decors))
        
        x0, y0 = LARGEUR_FENETRE + 20, 250
        rect_w, rect_h = 180, 45 * n_par_page + 60

        # Rectangle principal
        rectangle(x0, y0, x0 + rect_w, y0 + rect_h, couleur="black", remplissage="white")
        texte(x0 + rect_w // 2, y0 + 20, "Choisir un décor", taille=13, couleur="black", ancrage="center")

        # Affichage pagination
        if nbPages > 1:
            texte(x0 + rect_w // 2, y0 + 40, f"Page {page_actuelle + 1}/{nbPages}", couleur="black", taille=10, ancrage="center")
        
        # Affichage des décors
        for idx, position in enumerate(range(debut, fin)):
            decor = decors[position]
            yb = y0 + 60 + idx * 45
            rectangle(x0 + 10, yb, x0 + rect_w - 10, yb + 40, couleur='black', remplissage='light gray', epaisseur=1)
            texte(x0 + 80, yb + 20, decor.capitalize(), couleur='black', taille=12, ancrage='center')
            if biome == "S":
                chemin = f"decors/mer/{decor}.png"
            else:
                chemin = f"decors/terre/{decor}.png"
            image(x0 + 28, yb + 20, chemin, largeur=32, hauteur=32, ancrage='center')

        # Flèches pagination
        if nbPages > 1:
            # Flèche gauche (page précédente)
            if page_actuelle > 0:
                rectangle(x0 + 10, y0 + rect_h - 35, x0 + 50, y0 + rect_h - 10, couleur="black", remplissage="lightgray")
                polygone([(x0 + 20, y0 + rect_h - 22), (x0 + 40, y0 + rect_h - 32), (x0 + 40, y0 + rect_h - 12)], couleur="black", remplissage="black")
            # Flèche droite (page suivante)
            if page_actuelle < nbPages - 1:
                rectangle(x0 + rect_w - 50, y0 + rect_h - 35, x0 + rect_w - 10, y0 + rect_h - 10, couleur="black", remplissage="lightgray")
                polygone([(x0 + rect_w - 20, y0 + rect_h - 22), (x0 + rect_w - 40, y0 + rect_h - 32), (x0 + rect_w - 40, y0 + rect_h - 12)], couleur="black", remplissage="black")
        
        # Stocke nbPages pour la gestion des clics
        self.deco_nbPages = nbPages

    def afficheTuilesPossibles(self, x, y, bouton):
        self.choixPossibles = self.tuilesPossibles(x, y)
        self.caseChoisie = (x, y)
        self.indice = 0
        self.nbPages = (len(self.choixPossibles) + 4) // 5  # 5 tuiles par page
        self.menu_visible = True
        if len(self.choixPossibles) > 0:
            self.afficher_message_status(f"Tuiles possibles : {len(self.choixPossibles)}", duree=200, couleur="green")
        else:
            self.afficher_message_status("Aucune tuile possible", duree=200, couleur="red")

    def gerer_clic(self, x, y, bouton):
        if self.decos_menu_visible and self.decos_menu_info:
            i, j, biome, relx, rely = self.decos_menu_info
            decors = DECORS_PAR_BIOME[biome]
            n_par_page = 5
            nbPages = (len(decors) + n_par_page - 1) // n_par_page
            page_actuelle = self.deco_indice // n_par_page
            debut = page_actuelle * n_par_page
            fin = min(debut + n_par_page, len(decors))
            x0, y0 = LARGEUR_FENETRE + 20, 250
            rect_w, rect_h = 180, 45 * n_par_page + 60

            # Sélection d'un décor
            for idx, position in enumerate(range(debut, fin)):
                yb = y0 + 60 + idx * 45
                if x0 + 10 <= x <= x0 + rect_w - 10 and yb <= y <= yb + 40:
                    self.decors.append((i, j, relx, rely, decors[position]))
                    self.afficher_message_status(f"Décor '{decors[position]}' ajouté", couleur="green")
                    self.decos_menu_visible = False
                    self.mode_ajout_decor = False
                    self.deco_indice = 0
                    return

            # Gestion pagination
            # Flèche gauche (page précédente)
            if nbPages > 1 and x0 + 10 <= x <= x0 + 50 and y0 + rect_h - 35 <= y <= y0 + rect_h - 10 and page_actuelle > 0:
                self.deco_indice = max(0, self.deco_indice - n_par_page)
                return
            # Flèche droite (page suivante)
            if nbPages > 1 and x0 + rect_w - 50 <= x <= x0 + rect_w - 10 and y0 + rect_h - 35 <= y <= y0 + rect_h - 10 and page_actuelle < nbPages - 1:
                self.deco_indice = min(len(decors) - 1, self.deco_indice + n_par_page)
                return

            # Clique ailleurs = fermeture
            self.decos_menu_visible = False
            self.deco_indice = 0
            return

        # Gestion du bouton Ajout Décors
        if x >= LARGEUR_FENETRE:
            if (LARGEUR_FENETRE + 10 <= x <= LARGEUR_TOTALE - 10) and (HAUTEUR_FENETRE // 2 - 25 <= y <= HAUTEUR_FENETRE // 2 + 25):
                self.mode_ajout_decor = not self.mode_ajout_decor
                self.decos_menu_visible = False
                if self.mode_ajout_decor:
                    self.afficher_message_status("Mode Ajout Décor : Cliquez sur une tuile", couleur="blue")
                else:
                    self.afficher_message_status("Mode normal", couleur="green")
                return
            # Gestion du menu des tuiles
            if self.menu_visible and self.caseChoisie:
                page_actuelle = self.indice // 5
                debut = page_actuelle * 5
                fin = min(debut + 5, len(self.choixPossibles))
                for idx in range(debut, fin):
                    y_pos = 360 + ((idx - debut) * 45)
                    if 650 <= x <= 830 and y_pos <= y <= y_pos + 45:
                        ci, cj = self.caseChoisie
                        self.poser(ci, cj, self.choixPossibles[idx])
                        self.menu_visible = False
                        self.caseChoisie = None
                        return
                # Gestion pagination
                if self.nbPages > 1 and 605 <= y <= 625:
                    if 660 <= x <= 710 and page_actuelle > 0:
                        self.indice = max(0, self.indice - 5)
                        return
                    elif 770 <= x <= 820 and page_actuelle < self.nbPages - 1:
                        self.indice = min(len(self.choixPossibles) - 1, self.indice + 5)
                        return
            return

        # Gestion de l'ajout de décor
        if self.mode_ajout_decor:
            i, j = y // TAILLE_CASE, x // TAILLE_CASE
            if 0 <= i < NB_CASES and 0 <= j < NB_CASES and self.grille[i][j]:
                nom_tuile = self.grille[i][j]
                biomes = set(nom_tuile)
                biomes_dispo = [b for b in biomes if b in DECORS_PAR_BIOME]
                if not biomes_dispo:
                    self.afficher_message_status("Aucun décor pour ce biome", couleur="red")
                    return
                biome = biomes_dispo[0]
                relx = random.randint(16, TAILLE_CASE - 16)
                rely = random.randint(16, TAILLE_CASE - 16)
                self.decos_menu_visible = True
                self.decos_menu_info = (i, j, biome, relx, rely)
            return

        # Gestion normale: pose ou suppression de tuile
        i, j = y // TAILLE_CASE, x // TAILLE_CASE
        if 0 <= i < NB_CASES and 0 <= j < NB_CASES:
            if bouton == 1:
                self.afficheTuilesPossibles(i, j, bouton)
            elif bouton == 3:
                self.retirer(i, j)
                self.menu_visible = False
                self.caseChoisie = None

    def dessiner_menu(self):
        if not self.menu_visible or not self.choixPossibles:
            return

        # Grand rectangle principal (650,360 à 830,585)
        rectangle(650, 360, 830, 585, couleur="black", remplissage='white', epaisseur=2)
        
        # Lignes horizontales pour diviser en 5 rangées
        for i in range(1, 5):
            ligne(650, 360 + i * 45, 830, 360 + i * 45, couleur="black", epaisseur=1)

        page_actuelle = self.indice // 5
        debut = page_actuelle * 5
        fin = min(debut + 5, len(self.choixPossibles))

        # Afficher le numéro de page en haut du rectangle
        if self.nbPages > 1:
            texte(740, 352, f"Page {page_actuelle + 1}/{self.nbPages}",
                  couleur='black', taille=10, ancrage='center')

        # Afficher les tuiles
        for idx, position in enumerate(range(debut, fin)):
            if position < len(self.choixPossibles):
                code_tuile = self.choixPossibles[position]
                y_base = 360 + (idx * 45)
                y_centre = y_base + 22.5

                texte(665, y_centre, code_tuile, couleur='black', taille=10, ancrage='w')

                if code_tuile in self.tuiles:
                    try:
                        image(795, y_centre, self.tuiles[code_tuile],
                              largeur=35, hauteur=35, ancrage='center')
                    except:
                        texte(795, y_centre, "?", couleur='red', taille=16, ancrage='center')

        # Flèches de navigation en bas du rectangle
        if self.nbPages > 1:
            # Flèche gauche (page précédente)
            if page_actuelle > 0:
                rectangle(660, 605, 710, 625, couleur="black", remplissage="lightgray")
                polygone([(670, 615), (680, 605), (680, 625)], couleur="black", remplissage="black")

            # Flèche droite (page suivante)
            if page_actuelle < self.nbPages - 1:
                rectangle(770, 605, 820, 625, couleur="black", remplissage="lightgray")
                polygone([(810, 615), (800, 605), (800, 625)], couleur="black", remplissage="black")
    
    

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
                    if self.generer_carte_aleatoire():
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