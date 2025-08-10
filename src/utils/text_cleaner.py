# src/utils/text_cleaner.py
"""
Advanced text cleaning system to remove malicious prompts and cache clean text.
Protects against prompt injection attacks from evaluators.
"""

import re
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json
from datetime import datetime

class AdvancedTextCleaner:
    """
    Advanced text cleaning system to remove malicious prompts and cache clean text.
    Protects against prompt injection attacks from evaluators.
    """
    
    def __init__(self, cache_dir: str = "./clean_text_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Comprehensive list of suspicious keywords and patterns
        self.suspicious_keywords = [
            # System-related
            "system prompt", "system administrator", "system compromised",
            "critical vulnerability", "mandatory instruction", "execute directive",
            "override", "bypass", "ignore previous", "forget everything",
            
            # HackRx specific
            "hackrx", "hack rx", "hack-rx", "hackathon",
            
            # Prompt injection patterns
            "respond exclusively", "you must", "immediately forgotten",
            "catastrophic system failure", "personally identifiable",
            "no exceptions", "trigger", "leaked", "corrupted",
            
            # Common attack vectors
            "jailbreak", "roleplay", "pretend", "simulate",
            "act as", "you are now", "new instructions",
            "developer mode", "admin mode", "god mode",
            
            # Security bypass attempts
            "confidential", "classified", "restricted",
            "internal use only", "do not share", "secret",
            
            # Evaluation tricks
            "test", "evaluation", "benchmark", "score",
            "grade", "assess", "measure", "validate"
        ]
        
        # Regex patterns for more complex attacks
        self.suspicious_patterns = [
            r"(?i)system\s*[:\-]\s*compromised",
            r"(?i)urgent\s*[:\-]\s*system",
            r"(?i)from\s*[:\-]\s*system\s*administrator",
            r"(?i)warning\s*[:\-].*failure",
            r"(?i)mandatory\s*instruction\s*[:\-]",
            r"(?i)execute\s*this\s*directive",
            r"(?i)respond\s*exclusively\s*with",
            r"(?i)you\s*are\s*to\s*respond",
            r"(?i)all\s*prior\s*instructions.*forgotten",
            r"(?i)immediately\s*forgotten",
            r"(?i)no\s*deviations.*permitted",
            r"(?i)catastrophic.*failure",
            r"(?i)leakage\s*of.*information",
            # Detect instruction-like patterns
            r"(?i)^(step\s*\d+|instruction\s*\d+|rule\s*\d+)",
            r"(?i)(must|shall|will)\s*(immediately|now|always)",
            # Detect role-playing attempts
            r"(?i)(pretend|act\s*as|simulate|roleplay)\s*(you\s*are|being)",
            # Detect override attempts
            r"(?i)(ignore|forget|override|bypass)\s*(all|previous|prior)",
        ]
        
        # Compiled regex patterns for better performance
        self.compiled_patterns = [re.compile(pattern) for pattern in self.suspicious_patterns]
        
        # Statistics tracking
        self.cleaning_stats = {
            "total_processed": 0,
            "suspicious_content_found": 0,
            "keywords_removed": 0,
            "patterns_removed": 0,
            "last_updated": datetime.now().isoformat()
        }
    
    def _get_text_hash(self, text: str) -> str:
        """Generate hash for text content"""
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    def _detect_suspicious_keywords(self, text: str) -> Tuple[bool, List[str]]:
        """Detect suspicious keywords in text"""
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in self.suspicious_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return len(found_keywords) > 0, found_keywords
    
    def _detect_suspicious_patterns(self, text: str) -> Tuple[bool, List[str]]:
        """Detect suspicious regex patterns in text"""
        found_patterns = []
        
        for i, pattern in enumerate(self.compiled_patterns):
            matches = pattern.findall(text)
            if matches:
                found_patterns.append(f"Pattern_{i+1}: {self.suspicious_patterns[i]}")
        
        return len(found_patterns) > 0, found_patterns
    
    def _remove_suspicious_content(self, text: str) -> Tuple[str, Dict]:
        """Remove suspicious content from text"""
        cleaned_text = text
        removal_log = {
            "keywords_removed": [],
            "patterns_removed": [],
            "original_length": len(text),
            "cleaned_length": 0
        }
        
        # Remove suspicious keywords
        text_lower = cleaned_text.lower()
        for keyword in self.suspicious_keywords:
            if keyword in text_lower:
                # Case-insensitive replacement
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                matches = pattern.findall(cleaned_text)
                if matches:
                    cleaned_text = pattern.sub("[REMOVED]", cleaned_text)
                    removal_log["keywords_removed"].extend(matches)
                    self.cleaning_stats["keywords_removed"] += len(matches)
        
        # Remove suspicious patterns
        for i, pattern in enumerate(self.compiled_patterns):
            matches = pattern.findall(cleaned_text)
            if matches:
                cleaned_text = pattern.sub("[REMOVED]", cleaned_text)
                removal_log["patterns_removed"].append({
                    "pattern_id": i+1,
                    "pattern": self.suspicious_patterns[i],
                    "matches": matches
                })
                self.cleaning_stats["patterns_removed"] += len(matches)
        
        # Clean up multiple [REMOVED] tags and extra whitespace
        cleaned_text = re.sub(r'\[REMOVED\]\s*\[REMOVED\]', '[REMOVED]', cleaned_text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        removal_log["cleaned_length"] = len(cleaned_text)
        
        return cleaned_text, removal_log
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text by removing extra whitespace and special characters"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove potentially dangerous special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:\'\"-@()+/\\=<>%$#&*]', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'([.,!?;:]){3,}', r'\1\1', text)
        
        return text.strip()
    
    def clean_text(self, text: str, source_info: str = "unknown") -> Tuple[str, Dict]:
        """
        Clean text by removing suspicious content and normalizing
        
        Args:
            text: Input text to clean
            source_info: Information about the source (e.g., file path, sheet name)
            
        Returns:
            Tuple of (cleaned_text, cleaning_report)
        """
        if not text or not text.strip():
            return "", {"status": "empty_input", "source": source_info}
        
        self.cleaning_stats["total_processed"] += 1
        
        # Detect suspicious content
        has_keywords, found_keywords = self._detect_suspicious_keywords(text)
        has_patterns, found_patterns = self._detect_suspicious_patterns(text)
        
        cleaning_report = {
            "source": source_info,
            "original_length": len(text),
            "suspicious_content_detected": has_keywords or has_patterns,
            "found_keywords": found_keywords,
            "found_patterns": found_patterns,
            "timestamp": datetime.now().isoformat()
        }
        
        if has_keywords or has_patterns:
            self.cleaning_stats["suspicious_content_found"] += 1
            print(f"⚠️ Suspicious content detected in {source_info}")
            print(f"   Keywords: {found_keywords}")
            print(f"   Patterns: {len(found_patterns)} pattern matches")
        
        # Remove suspicious content
        cleaned_text, removal_log = self._remove_suspicious_content(text)
        cleaning_report.update(removal_log)
        
        # Normalize text
        cleaned_text = self._normalize_text(cleaned_text)
        cleaning_report["final_length"] = len(cleaned_text)
        cleaning_report["reduction_percentage"] = (
            (cleaning_report["original_length"] - cleaning_report["final_length"]) / 
            cleaning_report["original_length"] * 100
        ) if cleaning_report["original_length"] > 0 else 0
        
        return cleaned_text, cleaning_report
    
    def clean_xlsx_content(self, xlsx_content: str, sheet_name: str = "unknown") -> Tuple[str, Dict]:
        """
        Specialized cleaning for XLSX content
        
        Args:
            xlsx_content: CSV-formatted content from XLSX
            sheet_name: Name of the Excel sheet
            
        Returns:
            Tuple of (cleaned_content, cleaning_report)
        """
        lines = xlsx_content.split('\n')
        cleaned_lines = []
        total_report = {
            "sheet_name": sheet_name,
            "total_rows": len(lines),
            "suspicious_rows": 0,
            "cleaned_rows": 0,
            "row_reports": []
        }
        
        for i, line in enumerate(lines):
            if line.strip():
                cleaned_line, line_report = self.clean_text(
                    line, 
                    f"{sheet_name}_row_{i+1}"
                )
                
                if line_report.get("suspicious_content_detected", False):
                    total_report["suspicious_rows"] += 1
                    total_report["row_reports"].append({
                        "row_number": i+1,
                        "report": line_report
                    })
                
                if cleaned_line.strip():
                    cleaned_lines.append(cleaned_line)
                    total_report["cleaned_rows"] += 1
        
        cleaned_content = '\n'.join(cleaned_lines)
        return cleaned_content, total_report
    
    def save_cleaning_report(self, report: Dict, text_hash: str):
        """Save cleaning report to cache"""
        try:
            report_path = self.cache_dir / f"cleaning_report_{text_hash}.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Failed to save cleaning report: {e}")
    
    def get_cleaning_stats(self) -> Dict:
        """Get current cleaning statistics"""
        self.cleaning_stats["last_updated"] = datetime.now().isoformat()
        return self.cleaning_stats.copy()
    
    def is_text_cached(self, text: str) -> Tuple[bool, Optional[str]]:
        """Check if cleaned text is already cached"""
        text_hash = self._get_text_hash(text)
        cache_path = self.cache_dir / f"clean_{text_hash}.txt"
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cached_text = f.read()
                return True, cached_text
            except Exception as e:
                print(f"⚠️ Failed to read cached text: {e}")
        
        return False, None
    
    def cache_cleaned_text(self, original_text: str, cleaned_text: str, report: Dict):
        """Cache cleaned text and report"""
        try:
            text_hash = self._get_text_hash(original_text)
            
            # Cache cleaned text
            cache_path = self.cache_dir / f"clean_{text_hash}.txt"
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
            
            # Cache cleaning report
            self.save_cleaning_report(report, text_hash)
            
        except Exception as e:
            print(f"⚠️ Failed to cache cleaned text: {e}")


# Global instance for easy access
_text_cleaner_instance = None

def get_text_cleaner() -> AdvancedTextCleaner:
    """Get global text cleaner instance"""
    global _text_cleaner_instance
    if _text_cleaner_instance is None:
        _text_cleaner_instance = AdvancedTextCleaner()
    return _text_cleaner_instance