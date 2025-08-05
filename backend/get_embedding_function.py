import os
import requests
from dotenv import load_dotenv

# Load from .env file
load_dotenv()
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

HF_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def embed_text(text: str):
    if HF_API_KEY is None:
        raise ValueError("Missing Hugging Face API key in environment.")

    url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{HF_EMBEDDING_MODEL}"
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {"inputs": text}

    response = requests.post(url, headers=headers, json=json_data)
    response.raise_for_status()  # Will raise error for non-200 responses
    return response.json()
