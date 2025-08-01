from langchain_ollama.embeddings import OllamaEmbeddings


def get_embedding_function():
    return OllamaEmbeddings(model="mxbai-embed-large")