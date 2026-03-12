import time
timer = time.time()
print("Starting imports...")
import requests
from datetime import datetime
from docling_core.transforms.chunker import HierarchicalChunker
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

import traceback
print(f"Imports done in {time.time() - timer:.2f} seconds")

BASE_URL = "http://192.168.0.31:8080"

answer_prompt = """Act as a technical document analyst. Your goal is to give a clear and concise answer to the recruiter by providing relevant information and put forward the Maxime profile."""

def merge_consecutive_chunks(chunks):
    if not chunks:
        return []
    
    merged = []
    current = {"text": f"Titre: {chunks[0].meta.headings}, Texte: {chunks[0].text}", "heading": chunks[0].meta.headings}

    for next_chunk in chunks[1:]:
        if current["heading"] == next_chunk.meta.headings and \
           len(current["text"]) + len(next_chunk.text) < 2500:
            current["text"] += " " + next_chunk.text
        else:
            merged.append(current)
            current = {"text": f"Titre: {next_chunk.meta.headings}, Texte: {next_chunk.text}", "heading": next_chunk.meta.headings}

    merged.append(current)
    return merged

def envoyer_capsule(nom_fichier):
    """
    This function takes a file name as input, converts the document into a structured format using the DocumentConverter, and then sends the converted content to a specified endpoint for further processing. The function also includes error handling to manage any exceptions that may occur during the conversion or the HTTP request.
    """
    timer = time.time()
    print(f"Starting to process {nom_fichier}")

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = False
    
    format_options = {
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
    
    converter = DocumentConverter(format_options=format_options)
    print(f"DocumentConverter initialized in {time.time() - timer:.2f} seconds")

    timer = time.time()
    result = converter.convert(f"documents/{nom_fichier}")
    chunker = HierarchicalChunker(max_chars=2500)
    chunks = list(chunker.chunk(result.document))
    print(f"Document converted and chunked in {time.time() - timer:.2f} seconds")

    timer = time.time()
    final_chunks = merge_consecutive_chunks(chunks)
    print(f"Chunks created in {time.time() - timer:.2f} seconds")

    for chunk in final_chunks:
        print(f"Print text: {chunk['text'][:100]}...")
        timer = time.time()
        try:
            response = requests.post(f"{BASE_URL}/post", json={"contenu": chunk['text'], "nom_fichier": nom_fichier[:-4]}, timeout=6000)
            print(f"Status Code: {response.status_code}")
            print(f"Réponse : {response.text}")
            response.raise_for_status()
            print(f" Réponse : OK")
        except Exception as e:
            print(f" Erreur : {e}")
            traceback.print_exc()
        print(f"Chunk sent in {time.time() - timer:.2f} seconds")

if __name__ == "__main__":

    envoyer_capsule("CGAN.pdf")
    envoyer_capsule("Game_Jab_2023.pdf")
    envoyer_capsule("Cloud_computing.pdf")
    envoyer_capsule("Odoo_hackathon.pdf")
    envoyer_capsule("Opensourceproject.pdf")
    envoyer_capsule("Skijo_AI.pdf")
    envoyer_capsule("Vocabulary_generator.pdf")
    # timer2 = time.time()
    # chat_request("""When did Maxime start working at Oh Green ?""")
    # print(f"Chat request done in {time.time() - timer2:.2f} seconds")