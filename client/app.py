import time
timer = time.time()
print("Starting imports...")
import requests
from datetime import datetime

import traceback
print(f"Imports done in {time.time() - timer:.2f} seconds\n")

BASE_URL = "http://192.168.0.31:8080"

answer_prompt = """Act as a technical document analyst. Your goal is to give a clear and concise answer to the recruiter by answering only the question asked."""

def chat_request(message):
    time = datetime.now().strftime("%A %d %B %Y, %H:%M")
    prompt = f"""
    CURRENT DATE: {time}
    CONTEXT: You are the career advocate and AI representative for Maxime Devillet. Answer only based on the information you have about Maxime.but answer like a natural human would do with politeness. "
    """

    data = {"query": f"[The recruiter question]: {message}", "prompt": prompt}
    try:
        response = requests.post(f"{BASE_URL}/chat", json=data, stream=True)
        response.raise_for_status()
        for chunk in response.iter_content(decode_unicode=True):
            if chunk:
                print(chunk, end="", flush=True)

    except Exception as e:
        print(f"\n Erreur: {e}")

if __name__ == "__main__":

    timer2 = time.time()
    chat_request("""What strategy does Maxime suggest for achieving high-resolution results without directly training a model on high-resolution masks?""")
    print(f"\n\nChat request done in {time.time() - timer2:.2f} seconds")
