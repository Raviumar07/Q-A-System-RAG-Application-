from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from .embeddings import get_embedding_model

# Global FAISS store (in-memory for now)
vector_store = None

def create_or_load_vector_store(chunks):
    """
    Create FAISS vector store from document chunks
    """
    global vector_store

    embeddings = get_embedding_model()

    documents = [
        Document(
            page_content=chunk["text"],
            metadata={
                "source": chunk["source"],
                "chunk_id": chunk["chunk_id"],
                "chunk_info": chunk.get("chunk_info", f"Chunk {chunk['chunk_id']}")
            }
        )
        for chunk in chunks
    ]

    if vector_store is None:
        vector_store = FAISS.from_documents(documents, embeddings)
    else:
        vector_store.add_documents(documents)

    return vector_store


def get_vector_store():
    if vector_store is None:
        raise ValueError("Vector store not initialized")
    return vector_store
