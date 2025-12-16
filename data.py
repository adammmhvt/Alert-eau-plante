import requests
import json
import sqlite3

import os

SERVER_IP = "10.24.115.134"
URL = f"http://{SERVER_IP}:8000/api/data"
print("récupération des données à :", URL)

def recup_data():
	"""
	Récupérer les paraamètres de l'utilisateur
	"""
	response = requests.get(URL)
	data = response.json()

	return data


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BD_PATH = os.path.join(BASE_DIR, "Server/plante.db")

def transmettre_act_data(temp, hum, lum):
	"""
	Transmettre les données récupérés par le Raspberry à la base de données.
	"""
	conn = sqlite3.connect(BD_PATH)
	cursor = conn.cursor()

	cursor.execute("DELETE FROM actual_data") #supprimer les dernières données présents dans la tables
	cursor.execute( #ajouter les nouvelles données
		"INSERT INTO actual_data (act_temp, act_humidity, act_luminosity) VALUES (?, ?, ?)",
		(temp, hum, lum)
	    )

	conn.commit()
	conn.close()
