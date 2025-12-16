from EtatAlerte import *
from data import *
import time

#Récuperer données

data = recup_data()

if data["status"] == "ok":
			temp_min = data["temperature"]["min"]
			temp_max = data["temperature"]["max"]
			arrosage = data["arrosage"]
			lum = data["luminosity"]
			print("Paramètres mis à jour : ", temp_min, temp_max, arrosage, lum)


while True:
	act_temp, act_hum, act_lum = Alerte(temp_min, temp_max, arrosage, lum)
	
	#récuperer données toutes les 10 secondes
	sec = time.time()
	if round(sec)%5 == 0:
		data = recup_data()
		transmettre_act_data(act_temp, act_hum, act_lum)
		print("Données transmises")
		if data["status"] == "ok":
			temp_min = data["temperature"]["min"]
			temp_max = data["temperature"]["max"]
			arrosage = data["arrosage"]
			lum = data["luminosity"]
			print("Paramètres mis à jour : ", temp_min, temp_max, arrosage, lum)
	time.sleep(0.1)
	
	
	
	
