# 📄 Document Q&A Assistant (RAG Application)

A powerful Retrieval-Augmented Generation (RAG) system that allows you to upload PDF documents and websites, then ask questions and get AI-powered answers based on your content.

## 🌟 Features

- **📑 PDF Processing**: Upload and process multiple PDF documents
- **🌐 Website Scraping**: Extract content from web URLs (with SSL/bot protection handling)
- **🤖 AI-Powered Q&A**: Ask questions and get intelligent answers based on your documents
- **🔍 Semantic Search**: Advanced text chunking and embedding-based retrieval
- **📊 Source Attribution**: See exactly which documents and chunks were used for each answer
- **💬 Chat Interface**: User-friendly Streamlit frontend
- **🔄 Reset Functionality**: Clear documents and start fresh anytime

## 🏗️ Architecture

### Backend (FastAPI)
- **RESTful API** with automatic documentation
- **LangGraph** workflow orchestration
- **FAISS** vector database for similarity search
- **Azure OpenAI** integration for LLM responses
- **Hugging Face embeddings** with fallback options

### Frontend (Streamlit)
- **Interactive chat interface**
- **File upload with progress tracking**
- **Source detail expansion**
- **Real-time processing feedback**

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Azure OpenAI account (for LLM responses)
- 2GB+ RAM (for embedding models)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd "Q&A System(RAG Application)"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Mac/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```env
   # Azure OpenAI Configuration (for LLM responses)
   AZURE_OPENAI_API_BASE=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key
   AZURE_OPENAI_API_VERSION=2024-06-01
   AZURE_OPENAI_DEPLOYMENT_NAME=your-gpt-deployment-name
   
   # Optional: OpenAI API (alternative to Hugging Face embeddings)
   # OPENAI_API_KEY=your-openai-api-key
   ```

### Running the Application

1. **Start the Backend API**
   ```bash
   cd src/backend/api
   python main.py
   ```
   The API will be available at `http://localhost:8000`

2. **Start the Frontend** (in a new terminal)
   ```bash
   cd src/frontend
   streamlit run app.py
   ```
   The web interface will be available at `http://localhost:8501`

## 📖 Usage

### 1. Upload Documents
- **PDFs**: Click "Browse files" and select PDF documents
- **Websites**: Enter a URL in the text input

### 2. Process Content
- Click **"Process PDF Files"** after selecting PDFs
- Click **"Add URL"** after entering a website URL
- Wait for processing confirmation with chunk count

### 3. Ask Questions
- Type questions in the chat input
- Get AI-powered answers based on your uploaded content
- View source attribution and chunk details

### 4. Explore Sources
- Click **"🔍 View Source Details"** to see which document parts were used
- Review text previews from retrieved chunks
- Understand how answers were generated

## 🔧 Configuration

### Embedding Models
The system uses multiple embedding strategies with automatic fallback:

1. **Simple TF-IDF** (Default - offline, most reliable)
2. **Hugging Face Models** (Better quality, requires internet)
3. **OpenAI Embeddings** (Highest quality, requires API key)

### Chunking Parameters
Adjust in `src/backend/services/chunker.py`:
```python
chunk_size=800,      # Characters per chunk
chunk_overlap=100    # Overlap between chunks
```

### Vector Store
Uses FAISS for in-memory vector storage. For persistence, modify `src/backend/services/vector_store.py`.

## 📁 Project Structure

```
Q&A System(RAG Application)/
├── .env                           # Environment variables
├── requirements.txt               # Python dependencies
├── README.md                      # This file
└── src/
    ├── backend/
    │   ├── api/
    │   │   └── main.py           # FastAPI application
    │   ├── data/                 # Generated data storage
    │   │   ├── chunks/           # Text chunks (JSON)
    │   │   ├── pdfs/            # Processed PDFs
    │   │   └── webs/            # Web content cache
    │   ├── models/
    │   │   └── schemas.py        # Pydantic models
    │   ├── services/
    │   │   ├── chunker.py        # Text chunking logic
    │   │   ├── embeddings.py     # Embedding models
    │   │   ├── pdf_processor.py  # PDF text extraction
    │   │   ├── rag_retriever.py  # Document retrieval
    │   │   ├── vector_store.py   # FAISS vector operations
    │   │   └── web_processor.py  # Web scraping
    │   └── workflows/
    │       └── rag_workflow.py   # LangGraph RAG pipeline
    └── frontend/
        └── app.py                # Streamlit web interface
```

## 🛠️ API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `POST /upload/pdf` - Upload and process PDF files
- `POST /upload/url` - Process website URLs
- `POST /query` - Ask questions and get answers
- `POST /reset` - Reset system state
- `GET /status` - Get system statistics

### API Documentation
When running, visit `http://localhost:8000/docs` for interactive API documentation.

## 🔍 Troubleshooting

### Common Issues

**SSL Certificate Errors**
- The system automatically handles SSL issues in corporate networks
- Uses fallback mechanisms for both embeddings and web scraping

**403 Forbidden (Website Blocking)**
- Some sites block automated requests
- Try alternative URLs or copy content manually
- System provides helpful alternatives when blocked

**Memory Issues**
- Reduce `chunk_size` in chunker.py
- Use Simple TF-IDF embeddings instead of transformer models
- Process fewer documents at once

**Azure OpenAI Errors**
- Verify your deployment name matches your Azure setup
- Check API key and endpoint URL
- Ensure sufficient quota in your Azure account

### Performance Tips

1. **For Better Quality**: Add `OPENAI_API_KEY` for OpenAI embeddings
2. **For Speed**: Use Simple TF-IDF embeddings (default)
3. **For Memory**: Process documents individually
4. **For Accuracy**: Use smaller chunk sizes (400-600 characters)

## 🧪 Development

### Adding New Features

1. **New Document Types**: Extend `services/` with new processors
2. **Different Embeddings**: Modify `embeddings.py` 
3. **Enhanced UI**: Update `frontend/app.py`
4. **Custom Workflows**: Modify `workflows/rag_workflow.py`

### Testing
```bash
# Test backend API
curl http://localhost:8000/health

# Test with sample data
# Upload a PDF and ask: "What is machine learning?"
```

## 📦 Dependencies

### Core Framework
- **FastAPI** - Web API framework
- **Streamlit** - Frontend interface
- **LangChain** - LLM application framework
- **LangGraph** - Workflow orchestration

### AI/ML Libraries
- **OpenAI** - LLM integration
- **sentence-transformers** - Embedding models
- **FAISS** - Vector similarity search
- **scikit-learn** - TF-IDF embeddings

### Document Processing  
- **PyPDF** - PDF text extraction
- **BeautifulSoup4** - Web scraping
- **requests** - HTTP client

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source. Feel free to use, modify, and distribute.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the API documentation at `/docs`
3. Check server logs for detailed error messages

## 🔮 Future Enhancements

- [ ] Persistent vector storage (PostgreSQL + pgvector)
- [ ] Multiple file format support (Word, PowerPoint, etc.)
- [ ] Advanced conversation memory
- [ ] User authentication and document permissions
- [ ] Batch processing for large document sets
- [ ] Custom embedding model fine-tuning
- [ ] Export conversation history

---

Built with ❤️ using modern RAG architecture and best practices.
