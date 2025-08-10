# RAG Document Q&A System

A high-performance Retrieval-Augmented Generation (RAG) system for intelligent document question-answering with hybrid search capabilities and multi-modal support.

## 🚀 Quick Start

**Get started with setting up:** [📖 Setup Guide](SETUP.md)

## 🛠️ Tech Stack

### Core Framework
- **FastAPI** - High-performance async web framework
- **Python 3.11** - Modern Python with enhanced performance
- **Uvicorn** - Lightning-fast ASGI server

### AI/ML Components
- **BGE-M3** (`BAAI/bge-m3`) - State-of-the-art multilingual embedding model
- **BGE Reranker v2-M3** (`BAAI/bge-reranker-v2-m3`) - Advanced semantic reranking
- **Claude 3.5 Sonnet** - Primary LLM for text generation
- **Claude 3 Haiku** - Vision model for image analysis
- **Sentence Transformers** - Embedding framework
- **PyTorch** - Deep learning backend with CUDA support

### Vector Database & Search
- **FAISS** - Facebook AI Similarity Search for vector operations
- **Hybrid Search** - Combines semantic similarity + BM25 keyword matching
- **Advanced Caching** - Persistent embeddings and response caching

### Document Processing
- **PyMuPDF** - High-performance PDF processing
- **python-docx** - Microsoft Word document handling
- **python-pptx** - PowerPoint presentation processing
- **openpyxl** - Excel spreadsheet processing
- **BeautifulSoup4** - HTML/XML parsing
- **LangChain** - Document loading and text splitting

### Infrastructure
- **Docker** - Containerized deployment
- **Conda** - Environment management
- **Rich** - Enhanced terminal UI
- **Pydantic** - Data validation and settings management

## 🏛️ System Architecture & Modularity

### 📦 Modular Design
The system follows a **clean, modular architecture** with clear separation of concerns:

```
src/
├── 🧠 ai/              # AI models & prompts
├── 🌐 api/             # FastAPI endpoints & server
├── ⚙️  core/           # Configuration hub (❤️ Heart of system)
├── 📄 document_processing/  # Loaders & retrieval
├── 📊 models/          # Pydantic schemas
└── 🛠️  utils/          # Helpers & utilities
```

**Benefits:**
- 🔧 **Easy Maintenance** - Independent module updates
- 🚀 **Scalable Development** - Team can work on different modules
- 🧪 **Testable Components** - Isolated unit testing
- 🔄 **Reusable Code** - Modules can be used across projects

### ⚙️ Configuration System - Heart of the System ❤️

The **`src/core/config.py`** is the **central nervous system** that controls every aspect:

```python
# 🎯 Everything is configurable through centralized config classes
@dataclass
class ModelConfig:
    embedding_model: str = "BAAI/bge-m3"     # Switch embedding models
    llm_model: str = "anthropic/claude-3.5-sonnet"  # Change LLM
    device: str = "cuda"                      # GPU/CPU selection
    batch_size: int = 32                      # Processing batch size

@dataclass 
class RetrievalConfig:
    top_k_retrieval: int = 20                 # Search candidates
    semantic_weight: float = 0.7              # Hybrid search weights
    keyword_weight: float = 0.3               # BM25 influence
    use_reranking: bool = True                 # Enable/disable reranking
```

**🎛️ What You Can Configure:**
- 🤖 **AI Models** - Switch between any embedding/LLM models
- 🔍 **Search Parameters** - Tune hybrid search weights & thresholds
- 📊 **Processing Settings** - Chunk sizes, overlap, batch sizes
- 🚀 **Performance** - Rate limits, timeouts, cache settings
- 🛡️ **Security** - API keys, validation rules, content filters
- 📁 **Storage** - Cache directories, log paths, temp folders

**🔥 Dynamic Configuration:**
```python
# Change settings at runtime
config.update_config('retrieval', semantic_weight=0.8)
config.update_config('models', batch_size=64)
```

---

## ✨ Key Features

### 🔍 Hybrid Search Engine
- **Semantic Search**: Dense vector similarity using BGE-M3 embeddings
- **Keyword Search**: BM25 algorithm for exact term matching
- **Intelligent Fusion**: Configurable weights (70% semantic, 30% keyword)
- **Reranking**: BGE reranker for optimal result ordering

### 📄 Multi-Format Document Support
- **PDF**: Text extraction with page-level metadata
- **DOCX**: Full Word document processing
- **PPTX**: Slide content + AI-powered image analysis
- **XLSX**: Advanced spreadsheet processing with malicious content detection
- **HTML/TXT/CSV**: Web and plain text formats
- **EML**: Email message processing
- **Images**: Direct image analysis via vision models

### 🧠 Intelligent Processing Pipeline
- **Adaptive Strategy**: Automatically switches between RAG and full-text based on document size
- **Batch Processing**: Concurrent question processing for optimal performance
- **Smart Chunking**: Recursive text splitting with configurable overlap
- **Context Optimization**: Dynamic context window management

### 🚀 Performance Optimizations
- **GPU Acceleration**: CUDA support for embeddings and reranking
- **Async Processing**: Non-blocking I/O operations
- **Rate Limiting**: Configurable API call throttling
- **Memory Management**: Efficient caching and cleanup
- **Batch Embeddings**: Process multiple queries simultaneously

### 🛡️ Security & Reliability
- **Content Filtering**: Advanced malicious prompt detection
- **Input Validation**: Pydantic-based request validation
- **Error Handling**: Comprehensive exception management
- **Request Logging**: Detailed operation tracking
- **Fallback Mechanisms**: Graceful degradation on failures

## 🏗️ Pipeline Overview

### 1. Document Ingestion
```
URL Input → Download → Format Detection → Loader Selection → Content Extraction
```

### 2. Content Processing
```
Raw Content → Text Cleaning → Chunking (512 tokens, 150 overlap) → Metadata Enrichment
```

### 3. Embedding Generation
```
Text Chunks → BGE-M3 Encoder → 1024-dim Vectors → FAISS Index → Cache Storage
```

### 4. Query Processing
```
Questions → Batch Embedding → Hybrid Search → Candidate Retrieval → Reranking
```

### 5. Answer Generation
```
Context + Question → Document-Specific Prompts → Claude 3.5 → Response → Logging
```

## 🔧 System Architecture

### Core Components

**Document Processing Layer**
- Multi-format loaders with specialized parsers
- Intelligent text extraction and cleaning
- Metadata preservation and enrichment

**Embedding & Retrieval Layer**
- BGE-M3 multilingual embeddings (1024 dimensions)
- FAISS vector database with L2 similarity
- Hybrid search combining semantic + keyword matching
- BGE reranker for result optimization

**AI Inference Layer**
- Claude 3.5 Sonnet for text generation
- Claude 3 Haiku for vision tasks
- Document-specific system prompts
- Adaptive context management

**API & Service Layer**
- FastAPI with async request handling
- Rate limiting and request throttling
- Comprehensive error handling
- Real-time progress tracking

### Configuration Management
Centralized configuration system with:
- Model parameters and device allocation
- Processing thresholds and chunk sizes
- API endpoints and authentication
- Cache settings and cleanup policies
- Hybrid search weights and parameters

### Caching Strategy
- **Embedding Cache**: Persistent vector storage per document
- **Response Cache**: API response caching with TTL
- **Model Cache**: In-memory model instances
- **File Cache**: Temporary document storage with cleanup

## 🚦 Processing Flow

### Standard Document Flow
1. **Input Validation**: URL format and accessibility check
2. **Document Download**: Secure file retrieval with timeout
3. **Format Detection**: Extension-based loader selection
4. **Content Extraction**: Format-specific parsing
5. **Text Processing**: Cleaning, chunking, and metadata addition
6. **Embedding Generation**: BGE-M3 vectorization with GPU acceleration
7. **Index Creation**: FAISS index construction and caching
8. **Query Processing**: Batch question embedding and hybrid search
9. **Context Retrieval**: Top-k candidates with reranking
10. **Answer Generation**: LLM inference with document-specific prompts

### Special Processing Modes
- **Small Documents**: Direct full-text processing (< 5000 tokens)
- **Image URLs**: Direct vision model processing
- **PPTX Files**: Combined text + AI image analysis
- **Secret Tokens**: Special authentication handling
- **Flight Data**: Custom API integration

### Performance Optimizations
- **Concurrent Processing**: Parallel question handling
- **Memory Management**: GPU memory optimization with fallbacks
- **Batch Operations**: Efficient embedding generation
- **Smart Caching**: Multi-level cache hierarchy
- **Resource Pooling**: Connection and thread pool management

## 📊 Key Metrics & Thresholds

- **Chunk Size**: 512 tokens with 150 token overlap
- **Embedding Dimension**: 1024 (BGE-M3)
- **Retrieval**: Top-20 candidates → Top-10 after reranking
- **Context Limit**: 10,000 tokens maximum
- **Small Doc Threshold**: 5,000 tokens (bypass RAG)
- **Hybrid Weights**: 70% semantic, 30% keyword
- **Rate Limits**: 20 LLM calls, 1 image call concurrent
- **Cache TTL**: 24 hours with 10GB limit

This system delivers enterprise-grade document Q&A capabilities with state-of-the-art AI models, optimized for both accuracy and performance.