# src/api/server.py
"""FastAPI server configuration and setup"""

from fastapi import FastAPI
from ..ai import initialize_models
from .endpoints import hackathon_endpoint
from ..utils.terminal_ui import display_startup_info

# Initialize FastAPI app
app = FastAPI(
    title="RAG Document Q&A System",
    description="A modular document question-answering system using RAG",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    display_startup_info()
    print("📚 Initializing AI models...")
    initialize_models()
    print("\n✅ All systems ready! Server is now accepting requests.\n")

# Register endpoints
app.post("/hackrx/run")(hackathon_endpoint)