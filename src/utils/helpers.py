# src/utils/helpers.py
"""General utility functions"""

import json
import re
from datetime import datetime
from typing import List, Dict

from ..core.config import LOG_DIR

def log_request_and_response(request_data: dict, answers: List[str]):
    """Log API requests and responses"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        log_filename = LOG_DIR / f"request_log_{timestamp}.json"
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "request": {
                "documents": str(request_data.get("documents", "")),
                "questions": request_data.get("questions", []),
                "question_count": len(request_data.get("questions", []))
            },
            "response": {
                "answers": answers,
                "answer_count": len(answers)
            }
        }
        with open(log_filename, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Logging failed (non-critical): {e}")

def clean_text_for_llm(text: str, metadata: dict = None) -> str:
    """Clean text for LLM processing with advanced threat detection - ONLY for XLS files"""
    # Only apply malicious content cleaning for XLS files
    if metadata and metadata.get("cleaning_applied", False):
        # Text from XLS files has already been cleaned during loading
        return text
    
    # Check if this is from an XLS file by looking at the source URL
    if metadata and metadata.get("source"):
        source_url = str(metadata["source"]).lower()
        if source_url.endswith('.xlsx') or source_url.endswith('.xls'):
            # This is XLS content that somehow wasn't cleaned during loading
            # Apply cleaning as a safety measure
            from .text_cleaner import get_text_cleaner
            text_cleaner = get_text_cleaner()
            cleaned_text, cleaning_report = text_cleaner.clean_text(text, "llm_processing_xlsx")
            
            # Log if suspicious content was found
            if cleaning_report.get("suspicious_content_detected", False):
                print(f"🛡️ Suspicious content detected and cleaned in XLS content during LLM processing")
            
            return cleaned_text
    
    # For all other file types, return text as-is without malicious content cleaning
    return text