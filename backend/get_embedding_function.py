from langchain_ollama.embeddings import OllamaEmbeddings


def get_embedding_function():
    return OllamaEmbeddings(base_url="http://127.0.0.1:11434")