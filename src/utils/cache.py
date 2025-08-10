# src/utils/cache.py
"""Caching utilities for documents and questions"""

import pickle
import hashlib
import json
import numpy as np
import faiss
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any

from ..core.config import CACHE_DIR, EMBEDDING_MODEL_NAME

def get_url_hash(url: str) -> str:
    """Generate MD5 hash for URL"""
    return hashlib.md5(url.encode()).hexdigest()

def get_cache_paths(url_hash: str):
    """Get cache file paths for a URL hash"""
    model_name_slug = EMBEDDING_MODEL_NAME.replace("/", "_")
    return {
        'texts': CACHE_DIR / f"{url_hash}_{model_name_slug}_texts.pkl",
        'metadatas': CACHE_DIR / f"{url_hash}_{model_name_slug}_metadatas.pkl",
        'embeddings': CACHE_DIR / f"{url_hash}_{model_name_slug}_embeddings.npy",
        'index': CACHE_DIR / f"{url_hash}_{model_name_slug}_index.faiss",
        'info': CACHE_DIR / f"{url_hash}_{model_name_slug}_info.json"
    }

def save_to_cache(url: str, texts: List[str], metadatas: List[dict], embeddings: np.ndarray, index: Any):
    """Save document data to cache with enhanced PPTX support"""
    try:
        url_hash = get_url_hash(url)
        cache_paths = get_cache_paths(url_hash)
        with open(cache_paths['texts'], 'wb') as f: pickle.dump(texts, f)
        with open(cache_paths['metadatas'], 'wb') as f: pickle.dump(metadatas, f)
        np.save(str(cache_paths['embeddings']), embeddings)
        faiss.write_index(index, str(cache_paths['index']))
        
        # Enhanced cache info with PPTX processing details
        ai_analysis_count = sum(1 for meta in metadatas if meta.get('has_ai_analysis', False))
        total_images = sum(meta.get('image_count', 0) for meta in metadatas)
        
        cache_info = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'num_chunks': len(texts),
            'url_hash': url_hash,
            'model': EMBEDDING_MODEL_NAME,
            'enhanced_pptx': {
                'slides_with_ai_analysis': ai_analysis_count,
                'total_images_processed': total_images,
                'has_enhanced_content': ai_analysis_count > 0
            }
        }
        with open(cache_paths['info'], 'w') as f: json.dump(cache_info, f, indent=2)
        
        if ai_analysis_count > 0:
            print(f"💾 Cached enhanced PPTX data: {ai_analysis_count} slides with AI analysis, {total_images} images processed")
        else:
            print(f"💾 Cached document data for URL hash: {url_hash}")
    except Exception as e:
        print(f"⚠️ Failed to save cache: {e}")

def load_from_cache(url: str) -> tuple:
    """Load document data from cache"""
    try:
        url_hash = get_url_hash(url)
        cache_paths = get_cache_paths(url_hash)
        if not all(path.exists() for path in cache_paths.values()):
            return None, None, None, None
        with open(cache_paths['texts'], 'rb') as f: texts = pickle.load(f)
        with open(cache_paths['metadatas'], 'rb') as f: metadatas = pickle.load(f)
        _ = np.load(cache_paths['embeddings'])
        index = faiss.read_index(str(cache_paths['index']))
        with open(cache_paths['info'], 'r') as f: cache_info = json.load(f)
        print(f"📋 Loaded cached document: {cache_info['num_chunks']} chunks from persistent cache.")
        return texts, metadatas, None, index
    except Exception as e:
        print(f"⚠️ Failed to load cache: {e}")
        return None, None, None, None

def get_question_cache_path(doc_url: str, question: str) -> Path:
    """Get cache path for a document URL and question pair"""
    doc_hash = get_url_hash(doc_url)
    question_hash = hashlib.md5(question.encode()).hexdigest()
    return CACHE_DIR / f"q_{doc_hash}_{question_hash}.pkl"

def load_context_from_cache(path: Path) -> Optional[str]:
    """Load cached context string from file"""
    if path.exists():
        try:
            with open(path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load question cache from {path}: {e}")
    return None

def save_context_to_cache(path: Path, context: str):
    """Save context string to cache file"""
    try:
        with open(path, 'wb') as f:
            pickle.dump(context, f)
    except Exception as e:
        print(f"⚠️ Failed to save question cache to {path}: {e}")