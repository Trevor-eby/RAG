import requests

class RemoteEmbedding:
    def __init__(self, api_url: str):
        self.api_url = api_url

    def embed_query(self, text: str):
        response = requests.post(
            f"{self.api_url}/embed",  # adjust endpoint accordingly
            json={"text": text},
            timeout=10,
        )
        response.raise_for_status()
        embedding = response.json().get("embedding")
        if embedding is None:
            raise ValueError("Embedding not found in response")
        return embedding

    def embed_documents(self, texts: list[str]):
        response = requests.post(
            f"{self.api_url}/embed_batch",  # if your API supports batch embedding
            json={"texts": texts},
            timeout=10,
        )
        response.raise_for_status()
        embeddings = response.json().get("embeddings")
        if embeddings is None:
            raise ValueError("Embeddings not found in response")
        return embeddings

# Usage example:
def get_embedding_function():
    API_URL = "http://localhost:11434"  # replace with your actual URL
    return RemoteEmbedding(API_URL)
