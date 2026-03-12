import psycopg2
from flask import Flask, jsonify, request
from langchain_core.documents import Document
# from langchain_text_splitters import RecursiveCharacterTextSplitter
from docling_core.types.doc import DoclingDocument
from langchain_qdrant import QdrantVectorStore
from langchain_ollama import OllamaEmbeddings
from litellm import completion
import sys


app = Flask(__name__)
QDRANT_URL = "http://qdrant-server:6333"
COLLECTION_NAME = "ma_capsule_perso"
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://ollama-server:11434",
)

def process_chunk(chunk, query):
    """
    use the LLM to process the chunk of text and rewite it in a more concise way, keeping only the most important information.
    """
    try:
        response = completion(
            model="ollama/qwen2.5:7b",
            api_base="http://ollama-server:11434",
            temperature=0.1,
            max_tokens=300,
            messages=[
                {"role": "system", "content": query},
                {"role": "user", "content": chunk.page_content},
            ],
        )
        print(f"chunk content: {chunk.page_content}")
        print(f"LLM response: {response.choices[0].message.content}")
    except Exception as e:
        raise Exception(f"Error during LLM processing: {e}")
    return response.choices[0].message.content

@app.route("/save", methods=["POST"])
def save():
    """
    Entry point for saving content to the vector store. Expects a JSON payload with the following structure:
    {
        "content": "The text content to be processed and saved.",
        "nom_fichier": "optional_name_for_source",
    }
    The endpoint will split the content into chunks, process each chunk with the provided query, summarize it with the second query, and then save the results to the Qdrant vector store.
    """
    data = request.json
    if not data or "content" not in data:
        return jsonify({"error": "No content provided"}), 400
    
    
    try:
        content = data.get("content")
        name_project =data.get("nom_fichier", "unknown_project")

        doc = Document(
            page_content=content, 
            metadata={
                "source": name_project,
            }
        )

        QdrantVectorStore.from_documents(
            [doc],
            embeddings,
            url=QDRANT_URL,
            collection_name=COLLECTION_NAME,
        )

        return jsonify({"status": "saved"}), 201
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print("--- CRITICAL ERROR IN STORAGE ---")
        print(error_details) # Ceci apparaîtra enfin dans docker logs
        return jsonify({"error": str(e), "traceback": error_details}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
