from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
import os
import uvicorn

app = FastAPI()

#créer base de données

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) #récuperer,le dossier dans lequel se trouve le script python
BD_PATH = os.path.join(BASE_DIR, "plante.db") #créer ou accède au fichier plante.db peu importe la machine
print(BASE_DIR)

def init_bd():
    """
    Initialisation de la base de donées
    2 tables :
        parametres : enregistre les paramètres de l'utilisateur
        actual_data : enregistre les données mesurées par les capteurs
    """
    
    conn = sqlite3.connect(BD_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parametres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temp_min REAL,
            temp_max REAL,
            arrosage REAL,
            luminosity REAL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actual_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            act_temp REAL,
            act_humidity REAL,
            act_luminosity REAL
        )
    """)

    conn.commit()
    conn.close()

init_bd()



#Faire tourner le site web sur le serveur

STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
WEB_DIR = os.path.join(TEMPLATE_DIR, "index.html")
CONFIRMATION_DIR = os.path.join(TEMPLATE_DIR, "confirmation.html")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
def params(): #Page d'accueuil
    with open(WEB_DIR, "r", encoding="utf-8") as f:
        return f.read()
    
@app.get("/confirmation", response_class=HTMLResponse)
def confirmation(): #page de confiramation de l'envoi des parametres
    with open(CONFIRMATION_DIR, "r", encoding="utf-8") as f:
        return f.read()

from fastapi.responses import HTMLResponse
import sqlite3

@app.get("/data", response_class=HTMLResponse)
def data(): #page de visualisation des parametres
    conn = sqlite3.connect(BD_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM parametres")
    row = cursor.fetchone()   # Une seule ligne
    conn.close()

    # Aucune donnée
    if row is None:
        return """
        <html>
        <head>
            <title>Données Plantes</title>
            <style>
                body {
                    font-family: Arial;
                    margin: 40px;
                    background: #f0fff0;
                    text-align: center;
                }
                .msg {
                    font-size: 1.2rem;
                    color: #2e7d32;
                }
                a {
                    display: inline-block;
                    margin-top: 20px;
                    text-decoration: none;
                    padding: 10px 20px;
                    background-color: #43a047;
                    color: white;
                    border-radius: 8px;
                }
            </style>
        </head>
        <body>
            <h1>Aucune donnée disponible</h1>
            <p class="msg">Veuillez enregistrer des paramètres depuis la page principale.</p>
            <a href="/">Retour à l'accueil</a>
        </body>
        </html>
        """

    # row = (id, temp_min, temp_max, arrosage, luminosite)
    arrosage_txt = "Oui 🌧️" if row[3] == 1 else "Non 🚫"

    html = f"""
    <html>
    <head>
        <title>Données Plantes</title>
        <style>
            body {{
                font-family: Arial;
                margin: 40px;
                background: #f0fff0;
            }}
            h1 {{
                text-align: center;
                color: #2e7d32;
            }}
            table {{
                border-collapse: collapse;
                width: 60%;
                margin: auto;
            }}
            th, td {{
                border: 1px solid #2e7d32;
                padding: 12px;
                text-align: center;
            }}
            th {{
                background-color: #43a047;
                color: white;
            }}
            tr:nth-child(even) {{
                background-color: #d0f0c0;
            }}
            .btn {{
                display: block;
                width: fit-content;
                margin: 30px auto;
                padding: 10px 20px;
                background-color: #43a047;
                color: white;
                text-decoration: none;
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <h1>Paramètres actuels de la plante 🌱</h1>
        <table>
            <tr>
                <th>Température idéale</th>
                <th>Alerte arrosage</th>
                <th>Luminosité</th>
            </tr>
            <tr>
                <td>{row[1]} °C → {row[2]} °C</td>
                <td>{arrosage_txt}</td>
                <td>{row[4].capitalize()}</td>
            </tr>
        </table>
        <a href="/etat" class="btn">Ma plante</a>
        <a href="/" class="btn">Retour à l'accueil</a>
    </body>
    </html>
    """

    return html

    
@app.get("/etat", response_class=HTMLResponse)
def etat_plante(): #page de visualisation de l'état de la plante
    conn = sqlite3.connect(BD_PATH)
    cursor = conn.cursor()

    # Paramètres utilisateur
    cursor.execute("SELECT temp_min, temp_max, arrosage, luminosity FROM parametres")
    params = cursor.fetchone()

    # Données capteurs (dernière mesure)
    cursor.execute("SELECT act_temp, act_humidity, act_luminosity FROM actual_data")
    capteurs = cursor.fetchone()

    conn.close()

    if params is None or capteurs is None:
        return "<h1 style='text-align:center;'>Données insuffisantes</h1>"

    temp_min, temp_max, arrosage, lum_pref = params
    act_temp, act_hum, act_lum = capteurs
    
    print(params)
    
    #données affichage pour le site
    site_temp = round(act_temp, 1)
    site_hum = "Oui 💧" if act_hum == 1 and arrosage == 1 else "Non 🚫"
    site_lum = "Faible" if 0 < act_lum < 200 else "Moyenne" if 200 < act_lum < 500 else "Forte"

    # Message : état plante
    etat = "✅ Tout va bien"
    couleur = "#43a047"

    #vérification de l'état de la plante en fonction des paramètres et des mesures
    if act_temp < temp_min:
        etat = "❄️ Il fait trop froid"
        couleur = "#1e88e5"
    elif act_temp > temp_max:
        etat = "🔥 Il fait trop chaud"
        couleur = "#e53935"
    elif arrosage == 1 and act_hum == 1:
        etat = "💧 La plante a besoin d’eau"
        couleur = "#fb8c00"
    elif (lum_pref == "Faible" and act_lum > 200) or (lum_pref == "Moyenne" and act_lum > 500):
        etat = "🌞 Trop de lumière"
        couleur = "#fdd835"
    elif (lum_pref == "Forte" and act_lum < 500) or (lum_pref == "Moyenne" and act_lum < 200):
        etat = "🌑 Pas assez de lumière"
        couleur = "#6d4c41"

    # page html
    html = f"""
    <html>
    <head>
        <title>État de la plante</title>
        <style>
            body {{
                font-family: Arial;
                background: #f0fff0;
                padding: 40px;
            }}
            h1 {{
                text-align: center;
                color: #2e7d32;
            }}
            table {{
                border-collapse: collapse;
                width: 50%;
                margin: 30px auto;
            }}
            th, td {{
                border: 1px solid #2e7d32;
                padding: 12px;
                text-align: center;
            }}
            th {{
                background-color: #43a047;
                color: white;
            }}
            .etat {{
                width: 50%;
                margin: auto;
                padding: 25px;
                text-align: center;
                font-size: 1.4rem;
                font-weight: bold;
                color: white;
                border-radius: 15px;
                background-color: {couleur};
            }}
            .btn {{
                display: block;
                margin: 30px auto;
                padding: 10px 20px;
                background: #2e7d32;
                color: white;
                text-decoration: none;
                border-radius: 10px;
                width: fit-content;
            }}
        </style>
    </head>
    <body>

        <h1>Données actuelles de l'environnement</h1>

        <table>
            <tr>
                <th>Température (°C)</th>
                <th>Besoin d'arrosage</th>
                <th>Luminosité</th>
            </tr>
            <tr>
                <td>{site_temp}</td>
                <td>{site_hum}</td>
                <td>{act_lum}</td>
            </tr>
        </table>

        <div class="etat">
            {etat}
        </div>

        <a class="btn" href="/data">Mes paramètres</a>
        <a class="btn" href="/">Retour à l'accueil</a>

    </body>
    </html>
    """

    return html


@app.get("/api/data")
def api_data(): #page de récupération des paramètres du Raspberry
    conn = sqlite3.connect(BD_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM parametres ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()

    conn.close()

    if row is None:
        return {"status": "empty"}
    
    return {
        "status": "ok",
        "id": row[0],
        "temperature": {"min": row[1], "max": row[2]},
        "arrosage": row[3],
        "luminosity": row[4]
    }
    

@app.post("/save")
async def save( 
    temp_min:float = Form(...),
    temp_max:float = Form(...),
    arrosage:int = Form(...),
    luminosity:str = Form(...)
    ): #Récupération des paramètres de la page d'accueil pour les envoyer à la base de données

    print("Température :", (temp_min, temp_max))
    print("Arrosage :", arrosage)
    print('Luminosity :', luminosity)

    # Enregistrer dans sqlite
    conn = sqlite3.connect(BD_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM parametres") #supprimer les dernières données présents dans la tables
    cursor.execute( #ajouter les nouvelles données
        "INSERT INTO parametres (temp_min, temp_max, arrosage, luminosity) VALUES (?, ?, ?, ?)",
        (temp_min, temp_max, arrosage, luminosity)
    )

    conn.commit()
    conn.close()

    return RedirectResponse(url="/confirmation", status_code=303)
    #return {"status": "ok", "temp": temperature, "hum":humidity, "lum":luminosity}

	

#Lancer le serveur 

if __name__ == "__main__":
    uvicorn.run(app, host= "10.24.115.134", port=8000) #mettre bonne adresse en focntion du réseau
    #uvicorn.run(app)

    
