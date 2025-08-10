# 🚀 Setup Guide

## Prerequisites

- **Miniforge/Conda** - For environment management
- **CUDA-compatible GPU** (optional but recommended)
- **OpenRouter API Key** - For LLM access

## 📦 Installation Steps

### 1. Install Miniforge

**Windows:**
```bash
# Download and install Miniforge
winget install CondaForge.Miniforge3
```

**macOS:**
```bash
# Using Homebrew
brew install miniforge
```

**Linux:**
```bash
# Download installer
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh
```

### 2. Create Environment

```bash
# Create environment from yml file
conda env create -f environment.yml

# Activate environment
conda activate rag-qa-system
```

### 3. Configure Environment Variables

```bash
# Copy example env file
cp env.example .env

# Edit .env file with your API key
# OPENROUTER_API_KEY="your_actual_api_key_here"
# USER_ID="a03073d5-aabf-4306-9efa-bb5d93d95ad7"
```

### 4. Pre-cache Documents (Optional)

```bash
# Add URLs to cache in src/utils/document_urls.txt (one per line)
# Example:
# https://example.com/doc1.pdf
# https://example.com/doc2.docx

# Run cache manager to pre-process documents
python src/utils/cache_manager.py
```

### 5. Run the System

```bash
# Start the server
python main.py
```

## 🔧 Verification

The server will start on `http://localhost:8000`

**Test endpoint:**
```bash
curl -X POST "http://localhost:8000/hackrx/run" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://example.com/document.pdf",
    "questions": ["What is this document about?"]
  }'
```

## 🐛 Troubleshooting

**CUDA Issues:**
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"
```

**Missing Dependencies:**
```bash
# Reinstall environment
conda env remove -n rag-qa-system
conda env create -f environment.yml
```

**API Key Issues:**
- Ensure `.env` file exists in project root
- Verify OpenRouter API key is valid
- Check USER_ID matches the example format