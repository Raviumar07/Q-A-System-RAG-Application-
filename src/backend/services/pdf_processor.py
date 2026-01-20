import os
from langchain_community.document_loaders import PyPDFLoader

PDF_DIR = "backend/data/pdfs"


os.makedirs(PDF_DIR, exist_ok=True)

async def save_and_extract_pdf(file):
    """
        Save and extract text from a PDF file.
    """

    file_path = os.path.join(PDF_DIR, file.filename)

    # Read file content asynchronously
    content = await file.read()
    
    with open(file_path, "wb") as f:
        f.write(content)

    loader = PyPDFLoader(file_path)
    documents = loader.load()

    full_text = "\n".join([doc.page_content for doc in documents])

    return full_text