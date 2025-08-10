# src/utils/progress_tracker.py
"""
Progress tracking system for API requests
"""

import time
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ProgressStep:
    """Represents a single progress step"""
    name: str
    status: str = "pending"  # pending, in_progress, completed, failed
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    details: str = ""

class ProgressTracker:
    """Tracks progress of API request processing"""
    
    def __init__(self, request_id: str, total_questions: int):
        self.request_id = request_id
        self.total_questions = total_questions
        self.start_time = time.time()
        self.steps: List[ProgressStep] = []
        self.current_step_index = 0
        self.lock = threading.Lock()
        
        # Initialize standard steps
        self._initialize_steps()
    
    def _initialize_steps(self):
        """Initialize the standard processing steps"""
        steps = [
            "🔍 Analyzing request",
            "📥 Loading document", 
            "📝 Processing document",
            "🧠 Embedding content",
            "💾 Caching results",
            f"❓ Processing {self.total_questions} question{'s' if self.total_questions != 1 else ''}",
            "✅ Finalizing response"
        ]
        
        for step_name in steps:
            self.steps.append(ProgressStep(name=step_name))
    
    def start_step(self, step_name: str, details: str = ""):
        """Start a specific step"""
        with self.lock:
            # Find the step by name
            for i, step in enumerate(self.steps):
                if step_name in step.name:
                    step.status = "in_progress"
                    step.start_time = time.time()
                    step.details = details
                    self.current_step_index = i
                    break
            
            self._print_progress()
    
    def complete_step(self, step_name: str, details: str = ""):
        """Complete a specific step"""
        with self.lock:
            # Find the step by name
            for step in self.steps:
                if step_name in step.name:
                    step.status = "completed"
                    step.end_time = time.time()
                    if details:
                        step.details = details
                    break
            
            self._print_progress()
    
    def fail_step(self, step_name: str, error: str = ""):
        """Mark a step as failed"""
        with self.lock:
            # Find the step by name
            for step in self.steps:
                if step_name in step.name:
                    step.status = "failed"
                    step.end_time = time.time()
                    step.details = f"Error: {error}"
                    break
            
            self._print_progress()
    
    def update_question_progress(self, completed: int, total: int, current_question: str = ""):
        """Update progress for question processing"""
        with self.lock:
            # Find the question processing step
            for step in self.steps:
                if "Processing" in step.name and "question" in step.name:
                    step.status = "in_progress" if completed < total else "completed"
                    step.details = f"{completed}/{total} questions processed"
                    if current_question:
                        step.details += f" - Current: {current_question[:50]}..."
                    break
            
            self._print_progress()
    
    def _print_progress(self):
        """Print current progress to console"""
        elapsed = time.time() - self.start_time
        
        print(f"\n🚀 Request {self.request_id} - Progress Update ({elapsed:.1f}s elapsed)")
        print("=" * 60)
        
        for i, step in enumerate(self.steps):
            status_icon = {
                "pending": "⏳",
                "in_progress": "🔄",
                "completed": "✅",
                "failed": "❌"
            }.get(step.status, "❓")
            
            step_time = ""
            if step.start_time:
                if step.end_time:
                    duration = step.end_time - step.start_time
                    step_time = f" ({duration:.1f}s)"
                else:
                    duration = time.time() - step.start_time
                    step_time = f" ({duration:.1f}s...)"
            
            print(f"{status_icon} {step.name}{step_time}")
            if step.details:
                print(f"   └─ {step.details}")
        
        # Calculate overall progress
        completed_steps = sum(1 for step in self.steps if step.status == "completed")
        progress_percent = (completed_steps / len(self.steps)) * 100
        
        print(f"\n📊 Overall Progress: {progress_percent:.1f}% ({completed_steps}/{len(self.steps)} steps)")
        print("=" * 60)
    
    def get_progress_summary(self) -> Dict:
        """Get progress summary as dictionary"""
        with self.lock:
            completed_steps = sum(1 for step in self.steps if step.status == "completed")
            failed_steps = sum(1 for step in self.steps if step.status == "failed")
            in_progress_steps = sum(1 for step in self.steps if step.status == "in_progress")
            
            return {
                "request_id": self.request_id,
                "total_steps": len(self.steps),
                "completed_steps": completed_steps,
                "failed_steps": failed_steps,
                "in_progress_steps": in_progress_steps,
                "progress_percent": (completed_steps / len(self.steps)) * 100,
                "elapsed_time": time.time() - self.start_time,
                "steps": [
                    {
                        "name": step.name,
                        "status": step.status,
                        "details": step.details,
                        "duration": (step.end_time - step.start_time) if step.start_time and step.end_time else None
                    }
                    for step in self.steps
                ]
            }

# Global progress tracker storage
_active_trackers: Dict[str, ProgressTracker] = {}
_tracker_lock = threading.Lock()

def create_progress_tracker(request_id: str, total_questions: int) -> ProgressTracker:
    """Create a new progress tracker"""
    with _tracker_lock:
        tracker = ProgressTracker(request_id, total_questions)
        _active_trackers[request_id] = tracker
        return tracker

def get_progress_tracker(request_id: str) -> Optional[ProgressTracker]:
    """Get an existing progress tracker"""
    with _tracker_lock:
        return _active_trackers.get(request_id)

def remove_progress_tracker(request_id: str):
    """Remove a progress tracker when request is complete"""
    with _tracker_lock:
        if request_id in _active_trackers:
            del _active_trackers[request_id]

def get_all_active_trackers() -> Dict[str, Dict]:
    """Get summary of all active progress trackers"""
    with _tracker_lock:
        return {
            request_id: tracker.get_progress_summary()
            for request_id, tracker in _active_trackers.items()
        }