import sys

from flask import Flask, jsonify, request, Response
import requests
from flask_cors import CORS

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024
CORS(app)

SAVE_URL = "http://storage:5001"
CHAT_URL = "http://chatbot:5002"


@app.route("/")
def home():
    return "Welcome to the Gateway !"

@app.route("/post", methods=["POST"])
def post_message():
    """
    Endpoint to receive user data and forward it to the storage service. Expects a JSON payload with the following structure:
    {
        "contenu": "The text content to be processed and saved.",
        "nom_fichier": "optional_name_for_source",
    }
    The endpoint will forward the content and associated metadata to the storage service, which will handle the processing and saving of the data.
    """
    print(f"DEBUG: Taille du JSON reçu en RAM: {sys.getsizeof(request.data) / 1024 / 1024:.2f} MB")
    user_data = request.get_json()
    try:
        response = requests.post(
            f"{SAVE_URL}/save", json={"content": user_data["contenu"], "nom_fichier": user_data["nom_fichier"]}, timeout=6000
        )
        print(f"Storage response status: {response.status_code}")
        print(f"Storage response: {response.text}")
        response.raise_for_status()
        return jsonify({"gateway_status": "Transmis", "storage_response": response.text})
    except Exception as e:
        print(f"Gateway error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"gateway_status": "Erreur", "error": str(e)}), 500

@app.route("/chat", methods=["POST"])
def chat():
    """
    Endpoint to receive user queries and forward them to the chatbot service. Expects a JSON payload with the following structure:
    {
        "query": "The user's query or prompt to be processed by the chatbot.",
        "prompt": "Additional instructions or context for the chatbot to consider when generating a response."
    }
    The endpoint will forward the query and prompt to the chatbot service, which will process the input and return a response. The gateway will then return the chatbot's response to the user.
    """
    user_data = request.get_json()
    def generate_response():
        try:
            with requests.post(
                f"{CHAT_URL}/chat",
                json={"query": user_data.get("query", ""), "prompt": user_data.get("prompt", "")},
                timeout=420,
                stream=True
            ) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
                                if chunk:
                                    yield chunk
        except Exception as e:
            yield f"Erreur Gateway: {str(e)}"
    return Response(generate_response(), mimetype='text/plain')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
