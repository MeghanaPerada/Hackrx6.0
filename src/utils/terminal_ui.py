# src/utils/terminal_ui.py
"""Enhanced terminal UI with progress bars and system info"""

import time
import threading
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from ..core.config import config

class TerminalUI:
    """Enhanced terminal UI for RAG system"""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.current_request = None
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0
        }
    
    def display_startup_info(self):
        """Display system configuration on startup"""
        if not RICH_AVAILABLE:
            self._display_startup_simple()
            return
        
        # System Info Panel
        system_table = Table(show_header=False, box=None)
        system_table.add_column("Setting", style="cyan", width=20)
        system_table.add_column("Value", style="green")
        
        system_table.add_row("🚀 RAG System", "Starting...")
        system_table.add_row("🖥️  Device", config.models.device.upper())
        system_table.add_row("🌐 Server", f"{config.server.host}:{config.server.port}")
        system_table.add_row("📊 Workers", str(config.server.workers))
        
        # Model Info Panel
        model_table = Table(show_header=False, box=None)
        model_table.add_column("Model Type", style="cyan", width=15, no_wrap=True)
        model_table.add_column("Model Name", style="yellow", width=35, no_wrap=True)
        
        model_table.add_row("🧠 Embedding", config.models.embedding_model)
        model_table.add_row("🔄 Reranker", config.models.reranker_model)
        model_table.add_row("💬 Text LLM", config.models.llm_model)
        model_table.add_row("👁️  Vision LLM", config.models.llm_vision_model)
        
        # Processing Config Panel
        proc_table = Table(show_header=False, box=None)
        proc_table.add_column("Parameter", style="cyan", width=18, no_wrap=True)
        proc_table.add_column("Value", style="magenta", width=25, no_wrap=True)
        
        proc_table.add_row("📝 Chunk Size", f"{config.processing.chunk_size} tokens")
        proc_table.add_row("🔗 Chunk Overlap", f"{config.processing.chunk_overlap} tokens")
        proc_table.add_row("🎯 Top-K Retrieval", str(config.retrieval.top_k_retrieval))
        proc_table.add_row("🏆 Top-K Rerank", str(config.retrieval.top_k_rerank))
        proc_table.add_row("🪟 Context Window", f"{config.retrieval.max_context_tokens} tokens")
        proc_table.add_row("🔍 Hybrid Search", "✅" if config.retrieval.use_hybrid_search else "❌")
        
        # Create panels
        system_panel = Panel(system_table, title="🖥️ System Configuration", border_style="blue")
        model_panel = Panel(model_table, title="🤖 AI Models", border_style="green")
        proc_panel = Panel(proc_table, title="⚙️ Processing Configuration", border_style="yellow")
        
        # Display all panels
        self.console.print("\n")
        self.console.print(Align.center("🚀 RAG Document Q&A System", style="bold blue"))
        self.console.print(Align.center("━" * 60, style="blue"))
        self.console.print("\n")
        
        # Display panels vertically instead of horizontally
        self.console.print(system_panel)
        self.console.print(model_panel)
        self.console.print(proc_panel)
        self.console.print("\n")
        self.console.print(Align.center("✅ System Ready - Waiting for requests...", style="bold green"))
        self.console.print("━" * 80, style="blue")
        self.console.print("\n")
    
    def _display_startup_simple(self):
        """Fallback startup display without rich"""
        print("\n" + "="*80)
        print("🚀 RAG Document Q&A System - Starting...")
        print("="*80)
        print(f"🖥️  Device: {config.models.device.upper()}")
        print(f"🌐 Server: {config.server.host}:{config.server.port}")
        print(f"🧠 Embedding: {config.models.embedding_model}")
        print(f"💬 Text LLM: {config.models.llm_model}")
        print(f"👁️  Vision LLM: {config.models.llm_vision_model}")
        print(f"📝 Chunk Size: {config.processing.chunk_size} tokens")
        print(f"🎯 Top-K: {config.retrieval.top_k_retrieval}")
        print(f"🪟 Context: {config.retrieval.max_context_tokens} tokens")
        print("="*80)
        print("✅ System Ready - Waiting for requests...")
        print("="*80 + "\n")
    
    def create_request_progress(self, request_id: str, num_questions: int) -> Optional['RequestProgress']:
        """Create progress tracker for a request"""
        if not RICH_AVAILABLE:
            return SimpleProgress(request_id, num_questions)
        return RichProgress(request_id, num_questions, self.console)
    
    def log_request_start(self, doc_url: str, num_questions: int):
        """Log request start"""
        self.stats["total_requests"] += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if RICH_AVAILABLE:
            self.console.print(f"\n[bold blue]📥 [{timestamp}] New Request[/bold blue]")
            self.console.print(f"📄 Document: {doc_url[:60]}{'...' if len(doc_url) > 60 else ''}")
            self.console.print(f"❓ Questions: {num_questions}")
        else:
            print(f"\n📥 [{timestamp}] New Request")
            print(f"📄 Document: {doc_url}")
            print(f"❓ Questions: {num_questions}")
    
    def log_request_complete(self, success: bool, duration: float):
        """Log request completion"""
        if success:
            self.stats["successful_requests"] += 1
        else:
            self.stats["failed_requests"] += 1
        
        # Update average response time
        total = self.stats["successful_requests"] + self.stats["failed_requests"]
        self.stats["avg_response_time"] = (
            (self.stats["avg_response_time"] * (total - 1) + duration) / total
        )
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        status = "✅ Success" if success else "❌ Failed"
        
        if RICH_AVAILABLE:
            self.console.print(f"[bold green]{status}[/bold green] [{timestamp}] Duration: {duration:.2f}s")
            self.console.print("━" * 60, style="dim")
        else:
            print(f"{status} [{timestamp}] Duration: {duration:.2f}s")
            print("-" * 60)

class RequestProgress:
    """Base class for request progress tracking"""
    
    def __init__(self, request_id: str, num_questions: int):
        self.request_id = request_id
        self.num_questions = num_questions
        self.start_time = time.time()
    
    def update_step(self, step: str, message: str):
        pass
    
    def update_question_progress(self, current: int, total: int, message: str):
        pass
    
    def complete(self):
        pass
    
    def fail(self, error: str):
        pass

class SimpleProgress(RequestProgress):
    """Simple progress without rich"""
    
    def update_step(self, step: str, message: str):
        elapsed = time.time() - self.start_time
        print(f"[{elapsed:.1f}s] {step}: {message}")
    
    def update_question_progress(self, current: int, total: int, message: str):
        percent = (current / total) * 100 if total > 0 else 0
        print(f"Progress: {current}/{total} ({percent:.1f}%) - {message}")

class RichProgress(RequestProgress):
    """Rich progress with visual elements"""
    
    def __init__(self, request_id: str, num_questions: int, console: Console):
        super().__init__(request_id, num_questions)
        self.console = console
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        )
        self.main_task = None
        self.question_task = None
        self.live = None
    
    def start(self):
        """Start the progress display"""
        self.live = Live(self.progress, console=self.console, refresh_per_second=4)
        self.live.start()
        self.main_task = self.progress.add_task("🔄 Processing request...", total=100)
        return self
    
    def update_step(self, step: str, message: str):
        if self.main_task is not None:
            self.progress.update(self.main_task, description=f"{step}: {message}")
    
    def update_question_progress(self, current: int, total: int, message: str):
        if self.question_task is None and total > 0:
            self.question_task = self.progress.add_task("❓ Processing questions...", total=total)
        
        if self.question_task is not None:
            self.progress.update(self.question_task, completed=current, description=f"❓ {message}")
    
    def set_main_progress(self, percent: int):
        if self.main_task is not None:
            self.progress.update(self.main_task, completed=percent)
    
    def complete(self):
        if self.main_task is not None:
            self.progress.update(self.main_task, completed=100, description="✅ Request completed")
        if self.live:
            time.sleep(0.5)  # Show completion briefly
            self.live.stop()
    
    def fail(self, error: str):
        if self.main_task is not None:
            self.progress.update(self.main_task, description=f"❌ Failed: {error}")
        if self.live:
            time.sleep(1)  # Show error briefly
            self.live.stop()

# Global terminal UI instance
terminal_ui = TerminalUI()

def display_startup_info():
    """Display startup information"""
    terminal_ui.display_startup_info()

def create_request_progress(request_id: str, num_questions: int) -> RequestProgress:
    """Create request progress tracker"""
    return terminal_ui.create_request_progress(request_id, num_questions)

def log_request_start(doc_url: str, num_questions: int):
    """Log request start"""
    terminal_ui.log_request_start(doc_url, num_questions)

def log_request_complete(success: bool, duration: float):
    """Log request completion"""
    terminal_ui.log_request_complete(success, duration)