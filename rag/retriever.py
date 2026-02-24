from sentence_transformers import SentenceTransformer
import chromadb
from pathlib import Path

BASE_DIR = Path(__file__).parent
CHROMA_DIR = BASE_DIR.parent/ ".chroma"

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = chroma_client.get_or_create_collection(name = "telegram_messages")

def retrieve_context(query:str, top_k: int = 5) -> str:
    """
    Retreive top_k most relevant messages for the given query.
    Returns formatted string with retrieved messages.
    """

    try:
        if collection.count() == 0:
            return ""
        
        query_embedding = embedding_model.encode(query).tolist()
        results = collection.query(
            query_embeddings = [query_embedding],
            n_results = top_k
        )

        if not results['documents'] or not results['documents'][0]:
            return ""
        
        formatted = []
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]

        for doc, meta in zip(documents, metadatas):
            formatted.append(
                f"[{meta['date']} {meta['timestamp']}] {meta['role']}: {doc}"
            )
        return "\n".join(formatted)
    except Exception as e:
        print(f"[RAG ERROR] retrieve_context failed: {e}")  # visible in logs
        return ""
