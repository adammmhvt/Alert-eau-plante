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

def init_bd():
    conn = sqlite3.connect(BD_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parametres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temp_min REAL,
            temp_max REAL,
            hum_min REAL,
            hum_max REAL,
            luminosity REAL
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
def params():
    with open(WEB_DIR, "r", encoding="utf-8") as f:
        return f.read()
    
@app.get("/confirmation", response_class=HTMLResponse)
def confirmation():
    with open(CONFIRMATION_DIR, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/data", response_class=HTMLResponse)
def data():
    conn = sqlite3.connect(BD_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM parametres")
    row = cursor.fetchone()   # Une seule ligne
    conn.close()

    # Si aucune donnée n'est encore enregistrée
    if row is None:
        return """
        <html>
        <head>
            <title>Données Plantes</title>
            <style>
                body { font-family: Arial; margin: 40px; background: #f0fff0; }
                .msg { text-align: center; font-size: 1.2rem; color: #2e7d32; }
            </style>
        </head>
        <body>
            <h1 style="text-align:center;">Aucune donnée disponible</h1>
            <p class="msg">Veuillez enregistrer des paramètres depuis la page principale.</p>
        </body>
        </html>
        """

    # row = (id, temp_min, temp_max, hum_min, hum_max, lum)
    html = f"""
    <html>
    <head>
        <title>Données Plantes</title>
        <style>
            body {{ font-family: Arial; margin: 40px; background: #f0fff0; }}
            table {{ border-collapse: collapse; width: 70%; margin: auto; }}
            th, td {{ border: 1px solid #2e7d32; padding: 10px; text-align: center; }}
            th {{ background-color: #43a047; color: white; }}
            tr:nth-child(even) {{ background-color: #d0f0c0; }}
            h1 {{ text-align:center; color:#2e7d32; }}
        </style>
    </head>
    <body>
        <h1>Données enregistrées</h1>
        <table>
            <tr>
                <th>ID</th>
                <th>Température (min-max °C)</th>
                <th>Humidité (min-max %)</th>
                <th>Luminosité</th>
            </tr>
            <tr>
                <td>{row[0]}</td>
                <td>{row[1]} - {row[2]}</td>
                <td>{row[3]} - {row[4]}</td>
                <td>{row[5]}</td>
            </tr>
        </table>
    </body>
    </html>
    """

    return html


@app.get("/api/data")
def api_data():
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
        "humidity": {"min": row[3], "max": row[4]},
        "luminosity": row[5]
    }

#Récuperer les données du site web

@app.post("/save")
async def save(
    temp_min:float = Form(...),
    temp_max:float = Form(...),
    hum_min:float = Form(...),
    hum_max:float = Form(...),
    luminosity:str = Form(...)
    ):

    print("Température :", (temp_min, temp_max))
    print("Humidité :", (hum_min, hum_max))
    print('Luminosity :', luminosity)

    # Enregistrer dans sqlite
    conn = sqlite3.connect(BD_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM parametres") #supprimer les dernières données présents dans la tables
    cursor.execute( #ajouter les nouvelles données
        "INSERT INTO parametres (temp_min, temp_max, hum_min, hum_max, luminosity) VALUES (?, ?, ?, ?, ?)",
        (temp_min, temp_max, hum_min, hum_max, luminosity)
    )

    conn.commit()
    conn.close()

    return RedirectResponse(url="/confirmation", status_code=303)
    #return {"status": "ok", "temp": temperature, "hum":humidity, "lum":luminosity}


#Lancer le serveur 

if __name__ == "__main__":
    uvicorn.run(app, host= "10.24.115.108", port=8000) #mettre bonne adresse en focntion du réseau
    #uvicorn.run(app)