# backend/get_embedding_function.py

import os
import requests
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceHubEmbeddings

# Load from .env file
load_dotenv()
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
#HF_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def get_embedding_function():
    """
    Returns a function that can embed text using Hugging Face's API.
    This follows the factory pattern - returning a function rather than embeddings directly.
    """
    
    if not HF_API_KEY:
        raise ValueError("Missing Hugging Face API key in environment.")
    
    # Set up the API configuration once
    url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    
    def embed_text(text: str):
        """
        Embeds the given text using Hugging Face API and returns the embedding vector.
        
        Args:
            text (str): The text to embed
            
        Returns:
            list: The embedding vector
        """
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")
        
        json_data = {"inputs": text}
        
        try:
            response = requests.post(url, headers=headers, json=json_data, timeout=30)
            response.raise_for_status()  # Will raise error for non-200 responses
            
            result = response.json()
            
            # Handle different response formats from HF API
            if isinstance(result, list) and result:
                # If it's a list of embeddings, take the first one
                if isinstance(result[0], list):
                    return result[0]
                else:
                    return result
            else:
                raise ValueError(f"Unexpected response format: {result}")
                
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to get Hugging Face embedding: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error processing embedding response: {str(e)}")
    
    return embed_text