import argparse
import sys
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from langchain_community.document_loaders import PyPDFDirectoryLoader

from backend.get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""



def query_rag(query_text: str):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    # print(prompt)

    model = OllamaLLM(model="gemma3", host="host.docker.internal", port=11434)
    try:
        response_text = model.invoke(prompt)
    except Exception as e:
        print(f"Error calling model.invoke: {e}")
        response_text = "Sorry, there was an error processing your request."


    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"\nResponse: {response_text}\n\nSources: {sources}\n"
    print(formatted_response)
    sys.stdout.flush()
    return response_text

# CLI usage for debugging/testing
if __name__ == "__main__":
    ...
    #parser = argparse.ArgumentParser(description="Query RAG system from CLI")
    #parser.add_argument("query_text", type=str, help="The question to ask.")
    #args = parser.parse_args()

    #query_rag(args.query_text)