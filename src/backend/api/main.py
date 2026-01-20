import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import List, Optional
import uvicorn
import logging

# Import services
from services.pdf_processor import save_and_extract_pdf
from services.web_processor import fetch_and_clean_website
from services.chunker import chunk_text
from services.vector_store import create_or_load_vector_store
from services.rag_retriever import retrieve_relevant_chunks
from workflows.rag_workflow import graph

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Backend API",
    description="Retrieval-Augmented Generation Q&A System",
    version="1.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Health Check
# ---------------------------
@app.get("/health")
def health_check():
    """Check if the backend service is running"""
    return {
        "status": "healthy",
        "message": "RAG Backend API is running",
        "version": "1.0.0"
    }

# ---------------------------
# PDF Upload Endpoint
# ---------------------------
@app.post("/upload/pdf")
async def upload_pdf(files: List[UploadFile] = File(...)):
    """Upload and process PDF documents"""
    all_chunks = []
    
    for file in files:
        try:
            # Validate file type
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400, 
                    detail=f"File '{file.filename}' is not a PDF"
                )
            
            # Validate file size (10MB limit)
            content = await file.read()
            if len(content) > 10 * 1024 * 1024:  # 10MB
                raise HTTPException(
                    status_code=400,
                    detail=f"File '{file.filename}' exceeds 10MB limit"
                )
            
            # Reset file pointer for processing
            await file.seek(0)
            
            logger.info(f"Processing PDF: {file.filename}")
            
            # Process PDF and chunk the text
            text = await save_and_extract_pdf(file)
            chunks = chunk_text(text, source=file.filename)
            create_or_load_vector_store(chunks)
            all_chunks.extend(chunks)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing PDF {file.filename}: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Error processing PDF {file.filename}: {str(e)}"
            )
    
    return {
        "success": True,
        "message": f"Processed {len(files)} PDF(s) successfully",
        "total_chunks": len(all_chunks),
        "files_processed": [file.filename for file in files]
    }

# ---------------------------
# Website URL Ingestion
# ---------------------------
class URLRequest(BaseModel):
    url: str
    
    @validator('url')
    def validate_url(cls, v):
        if not v.strip():
            raise ValueError('URL cannot be empty')
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v.strip()

@app.post("/upload/url")
def upload_url(data: URLRequest):
    """Process and ingest website content"""
    try:
        logger.info(f"Processing URL: {data.url}")
        
        # Process website content and chunk the text
        text = fetch_and_clean_website(data.url)
        chunks = chunk_text(text, source=data.url.replace("/", "_"))
        create_or_load_vector_store(chunks)
        
        return {
            "success": True,
            "message": f"Website content from '{data.url}' processed and chunked successfully",
            "url": data.url,
            "total_chunks": len(chunks)
        }
        
    except Exception as e:
        logger.error(f"Error processing URL {data.url}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing URL: {str(e)}"
        )

# ---------------------------
# Question Answering
# ---------------------------
class QueryRequest(BaseModel):
    question: str
    chat_history: Optional[List[dict]] = []
    
    @validator('question')
    def validate_question(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty')
        return v.strip()

@app.post("/query")
def query_documents(data: QueryRequest):
    """Answer questions based on uploaded documents"""
    try:
        logger.info(f"Processing question: {data.question}")
        
        state = {
            "question": data.question,
            "chat_history": data.chat_history
        }

        # Run LangGraph workflow
        output_state = graph.invoke(state)

        return {
            "success": True,
            "question": data.question,
            "answer": output_state["answer"],
            "sources": [
                doc.metadata.get("source")
                for doc in output_state["retrieved_docs"]
            ],
            "source_details": [
                {
                    "source": doc.metadata.get("source"),
                    "chunk_info": doc.metadata.get("chunk_info", f"Chunk {doc.metadata.get('chunk_id', 'N/A')}"),
                    "preview": doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
                }
                for doc in output_state["retrieved_docs"]
            ],
            "total_chunks_retrieved": len(output_state["retrieved_docs"])
        }

    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------
# Reset System
# ---------------------------
@app.post("/reset")
def reset_system():
    """Reset the vector store and chat history"""
    try:
        logger.info("Resetting system...")
        
        # TODO: Add actual reset logic here
        # - Clear FAISS vector database
        # - Clear chat history
        # - Reset document metadata
        # - Clear any cached embeddings
        
        return {
            "success": True,
            "message": "System reset successfully - all documents and chat history cleared"
        }
        
    except Exception as e:
        logger.error(f"Error resetting system: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error resetting system: {str(e)}"
        )

# ---------------------------
# Get System Status
# ---------------------------
@app.get("/status")
def get_status():
    """Get current system status and statistics"""
    try:
        # TODO: Add actual status logic here
        # - Count of documents in vector store
        # - Vector database size
        # - Available models
        # - System health metrics
        
        return {
            "success": True,
            "documents_count": 0,  # Placeholder
            "vector_store_size": "0 MB",
            "embedding_model": "text-embedding-ada-002",
            "llm_model": "gpt-3.5-turbo",
            "status": "ready"
        }
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting status: {str(e)}"
        )

# ---------------------------
# Run the application
# ---------------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )
