# src/core/config.py
"""Central configuration hub - Heart of the RAG system"""

import os
import torch
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class APIConfig:
    """API endpoints and authentication"""
    openrouter_key: str = os.getenv("OPENROUTER_API_KEY", "")
    site_url: str = os.getenv("YOUR_SITE_URL", "")
    site_name: str = os.getenv("YOUR_SITE_NAME", "")
    user_id: str = os.getenv("USER_ID", "a03073d5-aabf-4306-9efa-bb5d93d95ad7")
    base_url: str = "https://backend.aikipedia.workers.dev"
    openrouter_url: str = "https://openrouter.ai/api/v1/chat/completions"
    aikipedia_chat_url: str = "https://backend.aikipedia.workers.dev/chat"
    flight_api_url: str = "https://register.hackrx.in/submissions/myFavouriteCity"
    timeout: int = 300
    llm_timeout: int = 120
    max_retries: int = 3
    llm_semaphore_limit: int = 20
    image_semaphore_limit: int = 1
    tiktoken_encoding: str = "cl100k_base"

@dataclass
class ModelConfig:
    """AI model specifications"""
    embedding_model: str = "BAAI/bge-m3"
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    llm_model: str = "anthropic/claude-3.5-sonnet"
    llm_vision_model: str = "anthropic/claude-3-haiku:beta"
    embedding_dim: int = 1024
    max_seq_length: int = 8192
    batch_size: int = 32
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    trust_remote_code: bool = True

@dataclass
class ProcessingConfig:
    """Document processing parameters"""
    chunk_size: int = 800
    chunk_overlap: int = 200
    small_doc_threshold: int = 5000
    max_file_size_mb: int = 100
    supported_formats: tuple = (".pdf", ".docx", ".pptx", ".xlsx", ".txt", ".md")
    max_concurrent_docs: int = 5

@dataclass
class RetrievalConfig:
    """RAG retrieval settings"""
    top_k_retrieval: int = 20
    top_k_rerank: int = 10
    similarity_threshold: float = 0.3
    rerank_threshold: float = 0.5
    max_context_tokens: int = 10000
    use_reranking: bool = True
    # Hybrid search settings
    use_hybrid_search: bool = True
    semantic_weight: float = 0.7
    keyword_weight: float = 0.3
    bm25_k1: float = 1.2
    bm25_b: float = 0.75
    min_keyword_matches: int = 1

@dataclass
class CacheConfig:
    """Caching system settings"""
    enabled: bool = True
    ttl_hours: int = 24
    max_cache_size_gb: int = 10
    cleanup_interval_hours: int = 6
    persist_embeddings: bool = True
    persist_responses: bool = True

@dataclass
class ServerConfig:
    """FastAPI server configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False
    log_level: str = "info"
    cors_origins: list = None
    rate_limit_per_minute: int = 60
    max_request_size_mb: int = 50

@dataclass
class PathConfig:
    """System paths and directories"""
    cache_dir: Path = Path("document_cache")
    log_dir: Path = Path("logs")
    temp_dir: Path = Path("temp")
    models_dir: Path = Path("models")
    
    def __post_init__(self):
        """Create directories on initialization"""
        for path in [self.cache_dir, self.log_dir, self.temp_dir, self.models_dir]:
            path.mkdir(exist_ok=True)

class SystemConfig:
    """Central configuration manager - Heart of the system"""
    
    def __init__(self):
        self.api = APIConfig()
        self.models = ModelConfig()
        self.processing = ProcessingConfig()
        self.retrieval = RetrievalConfig()
        self.cache = CacheConfig()
        self.server = ServerConfig()
        self.paths = PathConfig()
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate critical configuration"""
        if not self.api.openrouter_key:
            print("⚠️ Warning: OPENROUTER_API_KEY not found")
        if self.models.device == "cuda" and not torch.cuda.is_available():
            print("⚠️ Warning: CUDA requested but not available, falling back to CPU")
            self.models.device = "cpu"
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration for AI components"""
        return {
            "embedding_model": self.models.embedding_model,
            "reranker_model": self.models.reranker_model,
            "device": self.models.device,
            "batch_size": self.models.batch_size,
            "max_seq_length": self.models.max_seq_length
        }
    
    def get_api_headers(self) -> Dict[str, str]:
        """Get API headers for external requests"""
        return {
            "Authorization": f"Bearer {self.api.openrouter_key}",
            "HTTP-Referer": self.api.site_url,
            "X-Title": self.api.site_name,
            "Content-Type": "application/json"
        }
    
    def get_processing_params(self) -> Dict[str, Any]:
        """Get document processing parameters"""
        return {
            "chunk_size": self.processing.chunk_size,
            "chunk_overlap": self.processing.chunk_overlap,
            "max_file_size": self.processing.max_file_size_mb * 1024 * 1024,
            "supported_formats": self.processing.supported_formats
        }
    
    def get_retrieval_params(self) -> Dict[str, Any]:
        """Get RAG retrieval parameters"""
        return {
            "top_k": self.retrieval.top_k_retrieval,
            "rerank_k": self.retrieval.top_k_rerank,
            "similarity_threshold": self.retrieval.similarity_threshold,
            "max_context_tokens": self.retrieval.max_context_tokens,
            "use_hybrid": self.retrieval.use_hybrid_search,
            "semantic_weight": self.retrieval.semantic_weight,
            "keyword_weight": self.retrieval.keyword_weight,
            "bm25_k1": self.retrieval.bm25_k1,
            "bm25_b": self.retrieval.bm25_b
        }
    
    def update_config(self, section: str, **kwargs) -> None:
        """Dynamically update configuration"""
        if hasattr(self, section):
            config_obj = getattr(self, section)
            for key, value in kwargs.items():
                if hasattr(config_obj, key):
                    setattr(config_obj, key, value)
    
    def is_gpu_available(self) -> bool:
        """Check GPU availability"""
        return torch.cuda.is_available() and self.models.device == "cuda"
    
    def get_hybrid_search_config(self) -> Dict[str, Any]:
        """Get hybrid search specific configuration"""
        return {
            "enabled": self.retrieval.use_hybrid_search,
            "semantic_weight": self.retrieval.semantic_weight,
            "keyword_weight": self.retrieval.keyword_weight,
            "bm25_params": {
                "k1": self.retrieval.bm25_k1,
                "b": self.retrieval.bm25_b
            },
            "min_keyword_matches": self.retrieval.min_keyword_matches
        }
    
    def get_cache_path(self, doc_hash: str) -> Path:
        """Get cache file path for document"""
        return self.paths.cache_dir / f"{doc_hash}.pkl"
    
    def get_log_path(self, log_type: str = "app") -> Path:
        """Get log file path"""
        return self.paths.log_dir / f"{log_type}.log"

# Global configuration instance - Heart of the system
config = SystemConfig()

# Legacy compatibility exports
OPENROUTER_API_KEY = config.api.openrouter_key
USER_ID = config.api.user_id
API_BASE_URL = config.api.base_url
YOUR_SITE_URL = config.api.site_url
YOUR_SITE_NAME = config.api.site_name
EMBEDDING_MODEL_NAME = config.models.embedding_model
RERANKER_MODEL_NAME = config.models.reranker_model
API_BASE_URL = config.api.base_url
SMALL_DOC_TOKEN_THRESHOLD = config.processing.small_doc_threshold
CACHE_DIR = config.paths.cache_dir
LOG_DIR = config.paths.log_dir