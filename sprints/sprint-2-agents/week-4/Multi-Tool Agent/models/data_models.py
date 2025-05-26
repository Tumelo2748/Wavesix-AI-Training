"""
Data models for the legal assistant agent.
"""
from pydantic import BaseModel
from typing import List, Dict, Optional, Literal

class Clause(BaseModel):
    """Model for a clause in a contract."""
    text: str
    start_idx: int
    end_idx: int

class ClauseExtractionOutput(BaseModel):
    """Output model for extracted clauses."""
    clauses: List[Clause]

class ClassificationOutput(BaseModel):
    """Output model for clause classification."""
    category: Literal[
        "Data Collection", "Third-Party Sharing", "User Rights",
        "Liability Limitation", "Termination", "Jurisdiction", "Other"
    ]
    risk_level: Literal["low", "medium", "high"]
    summary: str

class FlaggedClause(BaseModel):
    """Model for clauses flagged for review."""
    clause: str
    reason: str

class DocumentSummary(BaseModel):
    """Output model for document summary."""
    overview: str
    key_points: List[str]
    risks: List[Dict[str, str]]

class SearchMatch(BaseModel):
    """Model for a search match."""
    text: str
    relevance: str

class SearchResult(BaseModel):
    """Output model for search results."""
    matches: List[Dict[str, str]]
    context: str

class ConversationContext(BaseModel):
    """Model for conversation context."""
    topic: str
    content: str
    timestamp: str

class AgentResponse(BaseModel):
    """Model for structured agent responses."""
    message: str
    flagged_clauses: Optional[List[FlaggedClause]] = None
    document_loaded: Optional[str] = None
    search_results: Optional[SearchResult] = None
    summary: Optional[DocumentSummary] = None