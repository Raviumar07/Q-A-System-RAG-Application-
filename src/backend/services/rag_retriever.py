from .vector_store import get_vector_store

def retrieve_relevant_chunks(query: str, top_k: int = 5):
    """
    Retrieve top-k relevant chunks for a query
    """
    vector_store = get_vector_store()
    docs = vector_store.similarity_search(query, k=top_k)
    return docs
