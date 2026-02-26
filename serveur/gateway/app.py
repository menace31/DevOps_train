from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

SAVE_URL = "http://storage:5001/save"

@app.route('/')
def home():
    return "Bienvenue sur le Gateway !"

@app.route('/post', methods = ['POST'])

def post_message():
    user_data = request.get_json()
    response = requests.post(SAVE_URL, json={"content": user_data['contenu']},timeout=5)
    return jsonify({"gateway_status": "Transmis", "storage_response": response.text})

@app.route('/messages', methods = ['GET'])
def get_messages():
    response = requests.get("http://storage:5001/messages",timeout=5)
    return response.text
if __name__ == "__main__":
    app.run(host = '127.0.0.1', port = "5000")