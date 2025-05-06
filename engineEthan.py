from fltk import *
import winsound
import time

winsound.PlaySound("media/nouveauTheme.wav", winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)
cree_fenetre(600, 600)

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

# Draw the clouds
for x, y in cloud_positions:
    image(x, y, "media/cloud.png", largeur=80, hauteur=80, ancrage='nw')

# Logo and buttons
image(300, 100, "media/logoMM.png", largeur=300, hauteur=300, ancrage='center')

# MapMaker
rectangle(200, 290, 400, 340, couleur='black', remplissage='white', epaisseur=2)
texte(300, 315, "MapMaker", couleur='black', taille=16, ancrage='center')


rectangle(550, 2, 600, 52, couleur='black', remplissage='white', epaisseur=2)
image(575, 27, "media/goSound.png", largeur=20, hauteur=20, ancrage='center', tag="isSound")
isSound = True





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
        elif 550 <= x <= 600 and 52 >= y >= 2:
            if isSound:
                isSound = False
                winsound.PlaySound(None, winsound.SND_PURGE)
                efface("isSound")
                image(575, 27, "media/stopSound.png", largeur=20, hauteur=20, ancrage='center', tag="isSound")
            else:
                isSound = True
                winsound.PlaySound("media/themeMM.wav", winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)
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
