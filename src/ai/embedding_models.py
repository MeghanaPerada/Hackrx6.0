# src/ai/embedding_models.py
"""ML model initialization and management"""

import torch
import warnings
import faiss
from sentence_transformers import SentenceTransformer
from sentence_transformers.cross_encoder import CrossEncoder

from ..core.config import EMBEDDING_MODEL_NAME, RERANKER_MODEL_NAME

# Suppress specific warnings
warnings.filterwarnings("ignore", message=".*encoder_attention_mask.*", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*legacy.*", category=FutureWarning)

# Device configuration - GPU for both embeddings and reranking
if torch.cuda.is_available():
    EMBEDDING_DEVICE = 'cuda'
    RERANKER_DEVICE = 'cuda'
    print(f"✅ GPU detected: {torch.cuda.get_device_name(0)}")
    print("🎯 Strategy: GPU for embeddings AND reranking (high performance mode)")
else:
    EMBEDDING_DEVICE = 'cpu'
    RERANKER_DEVICE = 'cpu'
    print("⚠️ Warning: No CUDA GPU detected. Using CPU for all operations.")

# Global model instances
embed_model = None
reranker_model = None

def initialize_models():
    """Initialize ML models with optimized GPU/CPU allocation"""
    global embed_model, reranker_model
    
    print(f"🔄 Loading BGE embedding model '{EMBEDDING_MODEL_NAME}' onto '{EMBEDDING_DEVICE.upper()}'...")
    # BGE-M3 on GPU for fast embedding generation
    embed_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=EMBEDDING_DEVICE, trust_remote_code=True)
    _ = embed_model.encode(["Warming up the BGE embedding model..."], show_progress_bar=False)
    print(f"✅ BGE embedding model loaded on {EMBEDDING_DEVICE.upper()}")

    print(f"🔄 Loading BGE reranker model '{RERANKER_MODEL_NAME}' onto '{RERANKER_DEVICE.upper()}'...")
    # BGE reranker on GPU for faster reranking
    try:
        reranker_model = CrossEncoder(RERANKER_MODEL_NAME, device=RERANKER_DEVICE, trust_remote_code=True)
        print(f"✅ BGE reranker model loaded on {RERANKER_DEVICE.upper()}")
    except RuntimeError as e:
        if "out of memory" in str(e).lower():
            print(f"⚠️ GPU memory insufficient for reranker, falling back to CPU...")
            reranker_model = CrossEncoder(RERANKER_MODEL_NAME, device='cpu', trust_remote_code=True)
            print(f"✅ BGE reranker model loaded on CPU (fallback)")
        else:
            raise e
    
    # FAISS uses CPU for stable and memory-efficient indexing/searching
    print("💻 FAISS configured for CPU-based similarity search (stable & memory-efficient)")

def get_embed_model():
    """Get the embedding model instance"""
    return embed_model

def get_reranker_model():
    """Get the reranker model instance"""
    return reranker_model

def get_device():
    """Get the current device (cuda/cpu)"""
    return EMBEDDING_DEVICE