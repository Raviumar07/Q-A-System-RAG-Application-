import os
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_DIR = "backend/data/chunks"
os.makedirs(CHUNK_DIR, exist_ok=True)

def chunk_text(text: str, source: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_text(text)

    chunk_data = []
    for idx, chunk in enumerate(chunks):
        chunk_data.append({
            "chunk_id": idx,
            "text": chunk,
            "source": source,
            "chunk_info": f"Chunk {idx+1} of {len(chunks)}"
        })

    file_path = os.path.join(CHUNK_DIR, f"{source}_chunks.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(chunk_data, f, indent=2)

    return chunk_data
