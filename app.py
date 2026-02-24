from flask import Flask,request,jsonify
from markupsafe import escape


app = Flask(__name__)

@app.route("/")
def home():
    return f"<p>Welcome to my Temporal capsule</p>"

@app.route("/status")
def get_status():
    return jsonify({"name":"capsule", "statut":"on line", "version":"1.0.0.0"})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001)