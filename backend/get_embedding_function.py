# backend/get_embedding_function.py
import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
MODEL_NAME_EMBEDDING = "sentence-transformers/all-MiniLM-L6-v2"

if not HF_API_KEY:
    raise ValueError("Missing Hugging Face API key in environment.")

client = InferenceClient(token=HF_API_KEY)

def get_embedding_function():
    def embed_text(text: str):
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")
        # The embed_text API expects a list of strings, returns list of embeddings
        embeddings = client.embed_text(model=MODEL_NAME_EMBEDDING, inputs=[text])
        # embeddings is a list of lists, take the first one
        return embeddings[0]
    return embed_text

    # if not HF_API_KEY:
    #     raise ValueError("Missing Hugging Face API key in environment.")
    
    # url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    # headers = {
    #     "Authorization": f"Bearer {HF_API_KEY}",
    #     "Content-Type": "application/json"
    # }

    # def embed_text(text: str):
    #     if not text or not isinstance(text, str):
    #         raise ValueError("Text must be a non-empty string")
    #     json_data = {"inputs": text}
    #     try:
    #         response = requests.post(url, headers=headers, json=json_data, timeout=30)
    #         response.raise_for_status()
    #         result = response.json()
    #         if isinstance(result, list) and result:
    #             if isinstance(result[0], list):
    #                 return result[0]
    #             else:
    #                 return result
    #         else:
    #             raise ValueError(f"Unexpected response format: {result}")
    #     except requests.exceptions.RequestException as e:
    #         raise RuntimeError(f"Failed to get Hugging Face embedding: {str(e)}")
    #     except Exception as e:
    #         raise RuntimeError(f"Error processing embedding response: {str(e)}")

    # # Wrapper class with embed_query method expected by Chroma
    # class HuggingFaceEmbedder:
    #     def embed_query(self, text: str):
    #         return embed_text(text)
    
    # return HuggingFaceEmbedder()
