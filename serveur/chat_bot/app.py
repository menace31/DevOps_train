import psycopg2
from ollama import Client
from flask import Flask, jsonify, request
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings



app = Flask(__name__)
client = Client(host='http://ollama-server:11434')
CHROMA_DIR = "./chroma_db"

embeddings = OllamaEmbeddings(
    model="nomic-embed-text", # Un modèle léger spécialisé dans les vecteurs
    base_url="http://ollama-server:11434"
)

@app.route('/feed')
def RAG_processus():

    conn = psycopg2.connect(
        host = 'db',
        database = 'capsule_db',
        user = 'user',
        password = 'password123'
    )

    cur = conn.cursor()
    
    cur.execute('SELECT content FROM messages;')

    rows = cur.fetchall()

    docs = [Document(page_content=row[0]) for row in rows]
    splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    separators=["\n\n", "\n", ".", " "])

    chunks = splitter.split_documents(docs)

    vector_store = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")

    conn.close()
    cur.close()

    return jsonify({
            "status": "Succès", 
            "chunks_created": len(chunks),
            "message": "Indexation terminée avec succès."
        })



@app.route('/chat',methods = ['POST'])
def ask_microservice():
    answere = request.get_json()
    query = answere.get('query','')
    prompt = answere.get('prompt','')
    if not query:
        return jsonify({"error": "Aucune question fournie"}), 400
    try:
        vector = Chroma(persist_directory =CHROMA_DIR, embedding_function = embeddings)

        docs = vector.similarity_search(query, k=3)

        context = "\n---\n".join([d.page_content for d in docs])

        system_prompt = f"""{prompt}
        CONTEXTE :
        {context}
        """
        print(f"DEBUG PROMPT ENVOYÉ : {system_prompt}")
        response = client.chat(model='qwen2.5:1.5b', messages=[
            {'role': 'system', 'content' : system_prompt},
            {'role': 'user', 'content': query}
        ])
        return response['message']['content']
    except Exception as e:
        return f"Erreur de communication : {e}"
    
if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = '5002')