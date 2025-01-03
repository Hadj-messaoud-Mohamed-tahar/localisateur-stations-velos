# Localisateur interactif des stations de vélos

## Description
Ce projet est une application web interactive permettant de localiser et d’obtenir des informations en temps réel sur les stations de vélos partagés à Lille, Toulouse, et Strasbourg.

## Fonctionnalités principales
- Affichage des stations de vélos sur une carte interactive.
- Recherche des stations proches d’une localisation donnée dans un rayon de 1 km.
- Conversion des adresses en coordonnées GPS grâce à l'API OpenCageData.
- Mise à jour automatique des données toutes les deux minutes.

## Technologies utilisées
- **Backend** : Python (Flask, SQLite, Requests, Schedule, Haversine)
- **Frontend** : HTML, CSS, JavaScript (Leaflet pour les cartes)
- **API utilisées** :
  - OpenCageData : Conversion des adresses en coordonnées GPS.
  - API des services de vélos des trois villes.

## Prérequis
1. Python (version 3.7 ou plus récente).
2. Une clé API OpenCageData.

## Installation
1. Clonez le dépôt :
   ```bash
   git clone https://github.com/yourusername/bike-station-locator.git
   cd bike-station-locator
