import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        host="db", database="capsule_db", user="user", password="password123"
    )


@app.route("/save", methods=["POST"])
def save():
    content = request.json.get("content")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (content) VALUES (%s)", (content,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "Sauvegardé"}), 201


@app.route("/messages", methods=["GET"])
def get_messages():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT content FROM messages;")
    row = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return row, 200


@app.route("/exec", methods=["POST"])
def execute_SQL():
    context = request.json.get("content")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(context)
    row = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": f"action efféctué {context} resultat: {row}"}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
