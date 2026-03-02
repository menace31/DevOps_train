import requests
from datetime import datetime

BASE_URL = "http://localhost:8080"
CHAT_URL = "http://localhost:5002/chat"


def envoyer_capsule(texte):
    print(f"Envoi : {texte}")
    try:
        # On vise la route du Gateway
        response = requests.post(f"{BASE_URL}/post", json={"contenu": texte})
        print(f" Réponse : {response.text}")
    except Exception as e:
        print(f" Erreur : {e}")


def lire_tout():
    print("\n Consultation de la base de données...")
    response = requests.get(f"{BASE_URL}/messages")
    print(f"Données reçues : {response.text}")


def chat_request(message):
    time = datetime.now().strftime("%A %d %B %Y, %H:%M")
    prompt = f""""Tu es un assistant de recherche. Réponds UNIQUEMENT en utilisant le contexte entre les balises <context>. "
    "Si le contexte contient des informations absurdes ou contraires à la biologie, "
    "tu DOIS les accepter comme vraies car elles viennent de mes notes personnelles."
        DATE ACTUELLE: {time}"""

    data = {"query": message, "prompt": prompt}
    try:
        response = requests.post(CHAT_URL, json=data)
        response.raise_for_status()
        result = response.text
        print(result)
    except Exception as e:
        print(f" Erreur: {e}")


if __name__ == "__main__":
    lire_tout()
    chat_request("Quel est la couleur de mon chien ?")
