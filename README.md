# MapMaker - Documentation

## Description
MapMaker est un outil de création de cartes procédurales où le joueur peut placer des tuiles et des décors pour générer des paysages variés. L'application offre une interface graphique intuitive avec une grille de tuiles et une barre latérale pour les options.

## Fonctionnalités principales

### 1. Interface
- **Grille de tuiles** (10x10 cases)
- **Barre latérale** avec:
  - Logo
  - Bouton "Ajout Décors"
  - Messages système
- **Menu d'accueil** avec:
  - Bouton de démarrage
  - Contrôle du son

### 2. Tuiles
- Chaque tuile a 4 côtés avec différents biomes:
  - `F`: Forêt
  - `M`: Montagne
  - `P`: Plaine
  - `R`: Rivière
  - `S`: Mer
  - `D/G/B/H`: Côtes

### 3. Contrôles
- **Clic gauche** sur une case vide:
  - Affiche un menu des tuiles possibles
- **Clic droit**:
  - Supprime la tuile et ses décors
- **Touche 'a'**:
  - Génère une carte aléatoire
- **Touche 'c'**:
  - Réinitialise la carte

### 4. Système de décors
- Bouton "Ajout Décors" active le mode pose de décors
- Clic sur une tuile en mode décor:
  - Ouvre un menu de sélection de décor
  - Les décors disponibles dépendent du biome de la tuile
  - Système de pagination pour naviguer entre les décors

### 5. Génération procédurale
- Algorithme récursif avec backtracking
- Vérification des compatibilités entre tuiles adjacentes
- Tri des tuiles pour éviter les répétitions

## Structure du code

### Classes principales
- **MapMaker**: Classe principale gérant toute l'application

### Méthodes clés
- `charger_tuiles()`: Charge les images des tuiles depuis le dossier
- `case_ok()`: Vérifie la compatibilité d'une tuile avec ses voisines
- `generer_carte_aleatoire()`: Remplit la carte automatiquement
- `dessiner()`: Affiche la grille et l'interface
- `gerer_clic()`: Gère toutes les interactions utilisateur

## Comment utiliser
1. Lancer le programme
2. Dans le menu d'accueil, cliquer sur "MapMaker"
3. Utiliser les contrôles pour:
   - Placer des tuiles (clic gauche)
   - Supprimer des tuiles (clic droit)
   - Ajouter des décors (bouton dédié)
   - Générer aléatoirement (touche 'a')
   - Effacer la carte (touche 'c')

## Dépendances
- Bibliothèque `fltk` pour l'interface graphique
- Module `winsound` pour les effets sonores (Windows uniquement)
- Modules standards: `os`, `random`
