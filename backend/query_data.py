import os
import sys
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

from backend.get_embedding_function import get_embedding_function

load_dotenv()

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
if not HF_API_KEY:
    raise ValueError("Missing HUGGINGFACE_API_KEY environment variable.")

HF_TEXT_GEN_MODEL = "gpt2"  # or any other model available for text generation

client = InferenceClient(token=HF_API_KEY)

def generate_text_hf(prompt: str, model: str = HF_TEXT_GEN_MODEL, max_tokens=200):
    output = client.text_generation(
        model=model,
        inputs=prompt,
        parameters={"max_new_tokens": max_tokens}
    )
    # output is usually a dict with 'generated_text'
    return output.get("generated_text", "").strip()

def query_rag(query_text: str):
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    results = db.similarity_search_with_score(query_text, k=5)
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in results])
    
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    try:
        response_text = generate_text_hf(prompt)
    except Exception as e:
        print(f"Error during text generation: {e}")
        response_text = "Sorry, there was an error processing your request."

    print("🔍 Prompt sent to Hugging Face text generation:\n", prompt)
    print("📨 Generated response:\n", response_text)

    sources = [doc.metadata.get("id", None) for doc, _ in results]
    formatted_response = f"\nResponse: {response_text}\n\nSources: {sources}\n"
    print(formatted_response)
    sys.stdout.flush()

    return response_text

if __name__ == "__main__":
    test_query = "What is the main topic of the documents?"
    print(query_rag(test_query))
