import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_embedding_model():
    """
    Returns embedding model - tries multiple options for reliability
    """
    # Option 1: Try simple TFIDF embeddings (most reliable, no internet needed)
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from langchain.embeddings.base import Embeddings
        from typing import List
        import numpy as np
        
        class SimpleTFIDFEmbeddings(Embeddings):
            """Simple TFIDF-based embeddings that work offline"""
            def __init__(self):
                self.vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                self.is_fitted = False
                self.documents_cache = []
            
            def embed_documents(self, texts: List[str]) -> List[List[float]]:
                """Embed a list of documents."""
                self.documents_cache.extend(texts)
                
                if not self.is_fitted:
                    self.vectorizer.fit(self.documents_cache)
                    self.is_fitted = True
                
                vectors = self.vectorizer.transform(texts).toarray()
                return vectors.tolist()
            
            def embed_query(self, text: str) -> List[float]:
                """Embed a single query."""
                if not self.is_fitted:
                    self.vectorizer.fit([text])
                    self.is_fitted = True
                
                vector = self.vectorizer.transform([text]).toarray()[0]
                return vector.tolist()
        
        print("Using simple TFIDF embeddings (offline)")
        return SimpleTFIDFEmbeddings()
    except Exception as e:
        print(f"Simple embeddings failed: {e}")
    
    # Option 2: Try Hugging Face (if network allows)
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        print("Attempting Hugging Face embeddings...")
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    except Exception as e:
        print(f"Hugging Face embeddings failed: {e}")
    
    # Option 3: Try OpenAI API (if API key available)
    try:
        from langchain_openai import OpenAIEmbeddings
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            print("Attempting OpenAI embeddings...")
            return OpenAIEmbeddings(
                model="text-embedding-3-small",
                openai_api_key=api_key
            )
    except Exception as e:
        print(f"OpenAI embeddings failed: {e}")
    
    raise Exception("All embedding options failed. Please check your network or add OPENAI_API_KEY.")