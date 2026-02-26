import requests
import time

BASE_URL = "http://localhost:8080"

def envoyer_capsule(texte):
    print(f"📤 Envoi : {texte}")
    try:
        # On vise la route du Gateway
        response = requests.post(f"{BASE_URL}/post", json={"contenu": texte})
        print(f"✅ Réponse : {response.text}")
    except Exception as e:
        print(f"❌ Erreur : {e}")

def lire_tout():
    print("\n📂 Consultation de la base de données...")
    # Ici, tu peux ajouter une route GET dans ton gateway pour voir les messages
    response = requests.get(f"{BASE_URL}/messages") # Si tu as créé cette route
    print(f"Données reçues : {response.text}")

if __name__ == "__main__":
    lire_tout()