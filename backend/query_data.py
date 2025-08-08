import os
import sys
import requests
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate

from backend.get_embedding_function import get_embedding_function

from dotenv import load_dotenv
load_dotenv()

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

# Set your HF text generation model here
HF_TEXT_GEN_MODEL = "gpt2"  # Replace with your chosen HF model for text generation, e.g. "gpt2", "bigscience/bloom"

def generate_text_hf(prompt: str, api_key: str, model: str = HF_TEXT_GEN_MODEL, max_tokens=200):
    """
    Sends a prompt to Hugging Face text generation API and returns the generated text.
    """
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "return_full_text": False,
        }
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        output = response.json()
        # Hugging Face generation outputs a list of dicts with 'generated_text' keys
        if isinstance(output, list) and "generated_text" in output[0]:
            return output[0]["generated_text"].strip()
        else:
            raise ValueError(f"Unexpected generation output format: {output}")
    except Exception as e:
        raise RuntimeError(f"Hugging Face text generation failed: {str(e)}")

def query_rag(query_text: str):
    # Get embedding function
    embedding_function = get_embedding_function()
    
    # Initialize Chroma vector store
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    
    # Search top 5 similar docs
    results = db.similarity_search_with_score(query_text, k=5)
    
    # Combine retrieved document contents as context
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    
    # Get Hugging Face API key from environment
    hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not hf_api_key:
        raise ValueError("Missing HUGGINGFACE_API_KEY environment variable.")
    
    # Generate answer from Hugging Face text generation API
    try:
        response_text = generate_text_hf(prompt, hf_api_key)
    except Exception as e:
        print(f"Error during text generation: {e}")
        response_text = "Sorry, there was an error processing your request."
    
    # Debug prints
    print("🔍 Prompt sent to Hugging Face text generation:\n", prompt)
    print("📨 Generated response:\n", response_text)
    
    # Optionally return response along with sources
    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"\nResponse: {response_text}\n\nSources: {sources}\n"
    print(formatted_response)
    sys.stdout.flush()
    
    return response_text

# CLI usage for debugging/testing
if __name__ == "__main__":
    query = "What is the main topic of the documents?"
    print(query_rag(query))
