#!/bin/bash

python3 Server/server.py > server.log 2>&1 &

echo "Le serveur se lance, musique d'introduction en cours..."

python3 Music.py

echo "Serveur lancé en Background"

python3 main.py