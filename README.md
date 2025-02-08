# Projet d'Informatique : Représentation et Compression d'Images

Ce projet fait partie du cours INFO-F-106 et se concentre sur la représentation et la compression d'images en utilisant un format personnalisé appelé ULBMP.

## Auteurs du projet

- Anthony Cnudde
- Gwenaël Joret
- Tom Lenaerts
- Robin Petit
- Loan Sens
- Cédric Simar

## Auteur du code `test.py` et solution

- william BATCHAYON
- Nyandjou Wilfried Larry 

## Description

Ce projet est divisé en plusieurs phases, chacune introduisant des fonctionnalités supplémentaires pour la manipulation et la compression d'images. Les principales phases sont :

1. **Format ULBMP 1.0** : Développement d'un format binaire simple pour encoder des images en RGB.
2. **Interface Graphique** : Création d'une interface graphique pour charger, afficher et enregistrer des images au format ULBMP.
3. **Compression RLE (ULBMP 2.0)** : Implémentation de la compression RLE pour réduire la taille des fichiers image.
4. **Profondeur des Pixels (ULBMP 3.0)** : Gestion des différentes profondeurs de couleur pour optimiser l'encodage des images.
5. **Différence avec les Pixels Précédents (ULBMP 4.0)** : Utilisation des différences entre pixels consécutifs pour améliorer la compression.

## Structure du Projet

- **pixel.py** : Classe `Pixel` pour représenter un pixel avec des valeurs RGB.
- **image.py** : Classe `Image` pour manipuler les images composées de pixels.
- **encoding.py** : Classes `Encoder` et `Decoder` pour encoder et décoder les images au format ULBMP.
- **window.py** : Interface graphique pour interagir avec les images ULBMP.
- **main.py** : Point d'entrée pour lancer l'interface graphique.
- **tests.py** : Un fichier pour tester les fonctionnalités du projet en s'arrurant que les codes respectent bien les instructions du project 

## Instructions d'Utilisation

1. **Installation des Dépendances** : Assurez-vous d'avoir Python et PySide6 installés sur votre machine.
2. **Exécution** : Lancez le script `main.py` pour ouvrir l'interface graphique.
3. **Utilisation de l'Interface** : Utilisez les boutons pour charger, afficher et enregistrer des images au format ULBMP.

## Contact

Pour toute question, veuillez me contacter.
