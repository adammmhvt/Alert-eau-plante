import RPi.GPIO as GPIO
import sys
import time
from grove.temperature import *
from grove.adc import ADC


class GroveLightSensor(object):
    '''
    Grove Light Sensor class

    Args:
        pin(int): number of analog pin/channel the sensor connected.
    '''
    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()

    @property
    def light(self):
        '''
        Get the light strength value, maximum value is 100.0%

        Returns:
            (int): ratio, 0(0.0%) - 1000(100.0%)
        '''
        value = self.adc.read(self.channel)
        return value


def Alerte(Tmin, Tmax, arrosage, lum):
	"""
	Vérifie les données et les envoie à la base de données
	"""
	global compteur_alternance, alerte_sonore
	
	#transformer données
	Dlum = {"Faible":(0, 200), 'Moyenne':(200, 500), 'Forte':(500, 1000)}
	lum_min, lum_max = Dlum[lum]
	
	# Récupérer les mesures des capteurs de température, luminosité et humidité
	actual_temp = Tsensor.temperature
	act_light = Lsensor.light 
	act_hum = GPIO.input(4)
	
	compteur_alternance += 1
	print(actual_temp, act_light, act_hum)
	
	#vérifier si les conditions de la plante sont respectées (en fonction des paramètres)
	if (not Tmin <= actual_temp <= Tmax) or (arrosage == 1 and act_hum == 1) or (not lum_min <= act_light <= lum_max): #si conditions pas respectées
		if not alerte_sonore: #Alerte
			pwm.start(3)
			GPIO.output(LED_PIN, 1)
			alerte_sonore = True
		else: #Alerte
			pwm.stop()
			GPIO.output(LED_PIN, 0)
			alerte_sonore = False
	else :  #si conditions respectées
		GPIO.output(LED_PIN, 0)
		alerte_sonore = False
		pwm.stop()
		
	time.sleep(0.5)
	
	return (actual_temp, act_hum, act_light)
	

GPIO.setmode(GPIO.BCM)

BUZZER_PIN = 16
LED_PIN = 5
TEMP_PIN = 0
LIGHT_PIN = 2
HUM_PIN = 4

GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(HUM_PIN, GPIO.IN)

pwm = GPIO.PWM(BUZZER_PIN, 440)
alerte_sonore = False

compteur_alternance = 0  # compteur pour alterner entre buzz/led actif et inactif

Tsensor = TemperTypedNTC(TEMP_PIN)
Lsensor = GroveLightSensor(LIGHT_PIN)




