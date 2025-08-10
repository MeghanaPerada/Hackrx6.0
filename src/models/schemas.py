# src/models/schemas.py
"""Pydantic models for API requests and responses"""

from pydantic import BaseModel, HttpUrl
from typing import List

class HackathonRequest(BaseModel):
    """Request model for the hackathon endpoint"""
    documents: HttpUrl
    questions: List[str]