# src/utils/security.py
"""Security utilities for path validation and sanitization"""

import os
from pathlib import Path
from urllib.parse import urlparse

def secure_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal"""
    # Remove path separators and dangerous characters
    filename = filename.replace('/', '_').replace('\\', '_')
    filename = filename.replace('..', '_').replace('~', '_')
    # Remove null bytes and control characters
    filename = ''.join(c for c in filename if ord(c) > 31 and c not in '<>:"|?*')
    return filename[:255]  # Limit length

def safe_join(base_path: Path, *paths: str) -> Path:
    """Safely join paths preventing traversal attacks"""
    result = base_path
    for path in paths:
        # Sanitize each path component
        clean_path = secure_filename(str(path))
        result = result / clean_path
    
    # Ensure result is within base_path
    try:
        result.resolve().relative_to(base_path.resolve())
        return result
    except ValueError:
        raise ValueError(f"Path traversal attempt detected: {result}")

def validate_url(url: str) -> bool:
    """Validate URL format and scheme"""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https') and bool(parsed.netloc)
    except Exception:
        return False