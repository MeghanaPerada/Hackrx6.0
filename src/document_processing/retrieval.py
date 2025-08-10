# src/document_processing/retrieval.py
"""Core RAG pipeline and document processing"""

import os
import numpy as np
import faiss
from pathlib import Path
from fastapi import HTTPException
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List

from .loaders import download_file, get_document_loader
from ..utils.cache import load_from_cache, save_to_cache
from ..ai.embedding_models import get_embed_model



# Global variables for document processing
faiss_index = None
processed_texts = []
processed_metadatas = []
last_processed_url = ""

def load_and_process_document(url: str):
    """Load and process document for RAG pipeline with progress tracking"""
    global faiss_index, processed_texts, processed_metadatas, last_processed_url
    if url == last_processed_url and faiss_index is not None:
        print(f"✅ Using cached document data for: {url}")
        return

    print(f"🔄 Processing document for RAG pipeline: {url}")
    

    cached_data = load_from_cache(url)
    if cached_data[0] is not None:
        processed_texts, processed_metadatas, _, faiss_index = cached_data
        last_processed_url = url
        return

    print("📥 Cache miss - processing document from scratch...")
    local_doc_path = download_file(url)
    if not local_doc_path:
        raise HTTPException(status_code=500, detail="Could not download document.")

    file_ext = Path(local_doc_path).suffix.lower()
    loader = get_document_loader(file_ext)
    if not loader:
        os.remove(local_doc_path)
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {file_ext}")

    raw_docs = loader(local_doc_path, url)
    if not raw_docs:
        os.remove(local_doc_path)
        raise HTTPException(status_code=500, detail="Could not load or parse the document.")

    print(f"📝 Splitting document into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=150)
    chunks = splitter.split_documents(raw_docs)
    processed_texts = [chunk.page_content for chunk in chunks]
    processed_metadatas = [chunk.metadata for chunk in chunks]

    embed_model = get_embed_model()
    print(f"🧠 Embedding {len(processed_texts)} chunks...")
    embeddings = embed_model.encode(processed_texts, batch_size=32, show_progress_bar=True)
    embeddings_np = np.array(embeddings).astype("float32")

    dimension = embeddings_np.shape[1]
    faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(embeddings_np)

    save_to_cache(url, processed_texts, processed_metadatas, embeddings_np, faiss_index)
    last_processed_url = url
    print("✅ Document processing complete and cached.")

    try:
        os.remove(local_doc_path)
        print(f"🗑️ Temporary file '{local_doc_path}' cleaned up.")
    except OSError as e:
        print(f"⚠️ Could not clean up temporary file: {e}")

def get_processed_data():
    """Get the current processed document data"""
    return faiss_index, processed_texts, processed_metadatas