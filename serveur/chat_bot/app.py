import os
import psycopg2
import time
from flask import Flask, jsonify, request, Response
import json
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_ollama import OllamaEmbeddings
from sentence_transformers import CrossEncoder
import litellm

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://ollama-server:11434",
)

app = Flask(__name__)
QDRANT_URL = "http://qdrant-server:6333"
COLLECTION_NAME = "ma_capsule_perso"
OLLAMA_BASE = os.getenv("OLLAMA_API_BASE", "http://ollama-server:11434")
try:
    client = QdrantClient(url=QDRANT_URL)
    vector = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME, embedding=embeddings)
    reranker = CrossEncoder('BAAI/bge-reranker-v2-m3', device='cuda')
except Exception as e:
    print(f"Error initializing Qdrant client or vector store: {e}")
    
@app.route("/chat", methods=["POST"])
def ask_microservice():
    """
    Endpoint to receive user queries and forward them to the chatbot service. Expects a JSON payload with the following structure:
    {
        "query": "The user's query or prompt to be processed by the chatbot.",
        "prompt": "Additional instructions or context for the chatbot to consider when generating a response."
    }
    The endpoint will forward the query and prompt to the chatbot service, which will process the input and return a response. The gateway will then return the chatbot's response to the user.
    """
    print("Received chat request")
    timer = time.time()
    answere = request.get_json()
    query = answere.get("query", "")
    prompt = answere.get("prompt", "")
    print(f"Initialisation des composants effectuée en {time.time() - timer:.2f} secondes")
    if not query:
        return jsonify({"error": "Aucune question fournie"}), 400
    
    try:
        timer = time.time()
        docs = vector.similarity_search(query, k=30)
        print(f"Recherche de similarité effectuée en {time.time() - timer:.2f} secondes")
        timer = time.time()
        pairs = [(query, doc.page_content) for doc in docs]
        scores = reranker.predict(pairs)

        score_merged = list(zip(scores, docs))
        score_merged.sort(key=lambda x: x[0], reverse=True)
        top_5 = [item[1] for item in score_merged[:5]]

        context = "\n".join([f"Nom du projet: {d.metadata.get('source', 'Inconnue')}\n CONTENU:{d.page_content}" for d in top_5])
        print(f"Contexte généré en {time.time() - timer:.2f} secondes")
        timer = time.time()
        system_prompt = f"""{prompt}CONTEXTE:\n{context}"""

        def generate_response():
            response = litellm.completion(
                model="ollama/qwen2.5:7b",
                api_base="http://ollama-server:11434",
                temperature=0.1,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                stream=True
            )
            for chunk in response:
                content = chunk.choices[0].delta.get("content", "")
                if content:
                    yield content
                
            print(f"Réponse générée en {time.time() - timer:.2f} secondes")
        return Response(generate_response(), mimetype='text/plain')
    
    except Exception as e:
        return f"Erreur de communication : {e}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)