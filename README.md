# Localisateur interactif des stations de vélos

## Description
Ce projet est une application web interactive permettant de localiser et d’obtenir des informations en temps réel sur les stations de vélos partagés à Lille, Toulouse, et Strasbourg.
![home](https://github.com/user-attachments/assets/6740e433-7213-4dca-ba96-c32d71bdb14a)
![image_2025-01-03_151840689](https://github.com/user-attachments/assets/4385b848-0006-4c2d-aee8-42e9b36fa724)      
![exemple_ville](https://github.com/user-attachments/assets/9e4730b7-139e-490c-8e3a-5f45e4248eba)


## Fonctionnalités principales
- Affichage des stations de vélos sur une carte interactive.
- Recherche des stations proches d’une localisation donnée dans un rayon de 1 km.
- Conversion des adresses en coordonnées GPS grâce à l'API OpenCageData.
- Mise à jour automatique des données toutes les deux minutes.

## Technologies utilisées

- **Backend** : Python (Flask, SQLite, Requests, Schedule, Haversine)
- **Frontend** : HTML, JavaScript (Leaflet pour les cartes)
- **API utilisées** :
  - OpenCageData : Conversion des adresses en coordonnées GPS.
  - API des services de vélos des trois villes.

## Prérequis
1. Python (version 3.7 ou plus récente).
2. Une clé API OpenCageData.

## Installation
1. Clonez le dépôt :
   ```bash
   git clone https://github.com/Hadj-messaoud-Mohamed-tahar/localisateur-stations-velos.git
   cd bike-station-locator
