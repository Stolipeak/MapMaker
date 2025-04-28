from fltk import *

# Play the theme music in a loop
son("media/theme.mp3", boucle=True)

cree_fenetre(600, 600)

# Background
rectangle(0, 0, 600, 600, couleur='sky blue', remplissage='sky blue')

# Coordinates for 30 clouds
cloud_positions = [
    (10, 10), (50, 50), (100, 100), (150, 150), (200, 200),
    (250, 250), (300, 300), (350, 350), (400, 400), (450, 450),
    (500, 10), (10, 500), (50, 450), (100, 400), (150, 350),
    (200, 300), (250, 200), (300, 100), (350, 50), (400, 10),
    (450, 100), (500, 200), (10, 300), (50, 400), (100, 500),
    (150, 450), (200, 400), (250, 350), (300, 250), (350, 150)
]

# Draw the clouds
for x, y in cloud_positions:
    image(x, y, "media/cloud.png", largeur=80, hauteur=80, ancrage='nw')

# Logo and buttons
image(300, 100, "media/logoMM.png", largeur=300, hauteur=300, ancrage='center')

rectangle(200, 250, 400, 300, couleur='black', remplissage='white', epaisseur=2)
texte(300, 275, "MapMaker", couleur='black', taille=16, ancrage='center')

rectangle(200, 310, 400, 360, couleur='black', remplissage='white', epaisseur=2)
texte(300, 335, "MapViewer", couleur='black', taille=16, ancrage='center')

# Event loop
while True:
    ev = attend_ev()
    tev = type_ev(ev)
    if tev == 'Quitte':
        break
    elif tev == 'ClicGauche':
        x, y = abscisse(ev), ordonnee(ev)
        if 200 <= x <= 400 and 300 >= y >= 250:
            print("MapMaker")
        elif 200 <= x <= 400 and 360 >= y >= 310:
            print("MapViewer")

        print(f"Clic gauche à ({x}, {y})")
    elif tev == 'ClicDroit':
        x, y = abscisse(ev), ordonnee(ev)
        print(f"Clic droit à ({x}, {y})")
    elif tev == 'Touche':
        t = touche(ev)
        print(f"Touche pressée : {t}")
    mise_a_jour()
ferme_fenetre()