import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8080"
CHAT_URL = "http://localhost:5002/chat"


def envoyer_capsule(texte):
    print(f"📤 Envoi : {texte}")
    try:
        # On vise la route du Gateway
        response = requests.post(f"{BASE_URL}/post", json={"contenu": texte})
        print(f" Réponse : {response.text}")
    except Exception as e:
        print(f" Erreur : {e}")

def update():
    print("\n mise à jour des connaissances de chat")
    try:
        response = requests.get(f"{BASE_URL}/update_data")
        print(response)
    except Exception as e:
        print(f" Erreur : {e}")

def lire_tout():
    print("\n Consultation de la base de données...")
    response = requests.get(f"{BASE_URL}/messages")
    print(f"Données reçues : {response.text}")

def chat_request(message):
    time = datetime.now().strftime("%A %d %B %Y, %H:%M")
    prompt = f"""Répond en anglais uniquement
        DATE ACTUELLE: {time}"""

    data = {'query':message, 'prompt':prompt}
    try:
        response = requests.post(CHAT_URL,json=data)
        response.raise_for_status()
        result = response.text
        print(result)
    except Exception as e:
        print(f" Erreur: {e}")
        

if __name__ == "__main__":
    lire_tout()
    update()
    chat_request("quel jour sommes nous ?")