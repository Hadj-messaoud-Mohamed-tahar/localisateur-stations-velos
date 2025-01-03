from flask import Flask, render_template, request, redirect, url_for, g
import pandas as pd
import requests
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
from math import radians, sin, cos, sqrt, atan2
app = Flask(__name__)
DATABASE = 'velo_info.db'

import json

def safe_json(obj):
    try:
        return json.dumps(obj)
    except TypeError as e:
        print(f"Erreur de sérialisation JSON : {e}")
        return json.dumps({})

# Fonction pour obtenir une connexion à la base de données
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        g._database = db
    return db
def get_coordinates(address):
    api_url = "https://api.opencagedata.com/geocode/v1/json"
    api_key = "6898b8f17e1c4ad2ae2407088a01cc36"  
    params = {"q": address, "key": api_key}
    response = requests.get(api_url, params=params)
    
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            geometry = results[0].get("geometry", {})
            return geometry.get("lat"), geometry.get("lng")
    
    return None, None
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Rayon de la Terre en km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Fonction pour extraire les données des APIs et mettre à jour la base
def update_database():
    # --- Lille ---
    url = "https://data.lillemetropole.fr/data/ogcapi/collections/vlille_temps_reel/items"
    limit = 289
    reponse = requests.get(url, params={"limit": limit})
    stations_info = []
    if reponse.status_code == 200:
        reponse = reponse.json()
        for feature in reponse.get("features", []):
            properties = feature.get("properties", {})
            station_info = {
                "nom_ville": "Lille",
                "Nom": properties.get("nom"),
                "Adresse": properties.get("adresse"),
                "Vélos disponibles": properties.get("nb_places_dispo"),
                "Places disponibles": properties.get("nb_velos_dispo"),
                "Latitude": feature.get("geometry", {}).get("coordinates", [])[1],
                "Longitude": feature.get("geometry", {}).get("coordinates", [])[0],
            }
            stations_info.append(station_info)
    dataframe = pd.DataFrame(stations_info)

    # --- Strasbourg ---
    url2 = "https://data.strasbourg.eu/api/explore/v2.1/catalog/datasets/stations-velhop/records?"
    reponse2 = requests.get(url2, params={"limit": 100}).json()
    stations_info2 = []
    for feature in reponse2.get("results", []):
        station_info = {
            "nom_ville": "Strasbourg",
            "Nom": feature.get("na"),
            "Adresse": feature.get("id"),
            "Vélos disponibles": feature.get("av"),
            "Places disponibles": feature.get("to"),
            "Latitude": feature.get("lat"),
            "Longitude": feature.get("lon"),
        }
        stations_info2.append(station_info)
    dataframe2 = pd.DataFrame(stations_info2)

    # --- Toulouse ---
    url1 = "https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets/api-velo-toulouse-temps-reel/records?"
    rows_per_page = 10
    start = 0
    stations_info1 = []
    while True:
        reponse1 = requests.get(url1, params={"start": start, "rows": rows_per_page}).json()
        for feature in reponse1.get("results", []):
            station_info1 = {
                "nom_ville": "Toulouse",
                "Nom": feature.get("name"),
                "Adresse": feature.get("address"),
                "Vélos disponibles": feature.get("available_bikes"),
                "Places disponibles": feature.get("available_bike_stands"),
                "Latitude": feature.get("position", {}).get("lat", []),
                "Longitude": feature.get("position", {}).get("lon", []),
            }
            stations_info1.append(station_info1)
        start += rows_per_page
        if len(reponse1.get("results", [])) < rows_per_page:
            break
    dataframe1 = pd.DataFrame(stations_info1)

    # Fusionner les données
    data = pd.concat([dataframe, dataframe1, dataframe2], ignore_index=True)
    data.dropna(inplace=True)

    # Mise à jour de la base de données SQLite
    conn = sqlite3.connect(DATABASE)
    table_name = "velo"
    data.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()

# Page d'accueil pour choisir une ville

@app.route('/', methods=['GET',"post"])
def index():
    if request.method == 'POST':
        # Vérifiez si l'utilisateur veut rechercher par ville ou par proximité
        if 'ville' in request.form:
            ville = request.form['ville']
            return redirect(url_for('afficher_ville', ville=ville))
    return render_template('index.html')

@app.route('/proximite', methods=['GET', 'POST'])
def proximite():
    if request.method == 'POST':
        # Récupérer l'adresse fournie par l'utilisateur
        user_address = request.form['adresse']
        user_lat, user_lon = get_coordinates(user_address)
        if user_lat is None or user_lon is None:
            return "Adresse introuvable. Veuillez réessayer.", 400

        # Charger les stations depuis la base de données
        db = get_db()
        query = "SELECT Nom, Latitude, Longitude, `Vélos disponibles`, `Places disponibles`, nom_ville FROM velo"
        stations = db.execute(query).fetchall()
        stations = [dict(station) for station in stations]

        # Filtrer les stations dans un rayon de 1 km
        stations_proches = []
        for station in stations:
            if station['Latitude'] is not None and station['Longitude'] is not None:
                distance = haversine(user_lat, user_lon, station['Latitude'], station['Longitude'])
                if distance <= 1:
                    stations_proches.append(station)

        print(stations_proches)  # Log des stations proches
        return render_template(
            'proximite_map.html',
            stations=stations_proches,
            user_lat=user_lat,
            user_lon=user_lon,
            adresse=user_address
        )
    return redirect('/')
    

# Route pour afficher les stations d'une ville spécifique
@app.route('/<ville>')
def afficher_ville(ville):
    db = get_db()
    query = "SELECT Nom, Latitude, Longitude, `Vélos disponibles`, `Places disponibles` FROM velo WHERE nom_ville LIKE ?"
    stations = db.execute(query, (f"%{ville}%",)).fetchall()
    stations = [dict(station) for station in stations]
    return render_template('ville.html', ville=ville.capitalize(), stations=stations)

# Planifier la mise à jour de la base de données toutes les heures
scheduler = BackgroundScheduler()
scheduler.add_job(update_database, 'interval', minutes=2)
scheduler.start()

# Démarrer le serveur Flask
if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        # Arrêter le planificateur de tâches lorsque l'application se ferme
        scheduler.shutdown()

