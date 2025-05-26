"""
Search tools for the legal assistant agent.
"""
from typing import List, Dict
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Import models from the models module
from models.data_models import SearchResult, ConversationContext

def search_document(text: str, query: str) -> SearchResult:
    """Search for specific terms or topics in the document."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = text_splitter.split_text(text)
    
    matches = []
    for chunk in chunks:
        if query.lower() in chunk.lower():
            matches.append({
                "text": chunk,
                "relevance": "high" if chunk.lower().count(query.lower()) > 1 else "medium"
            })
    
    return SearchResult(
        matches=matches[:5],  # Return top 5 matches
        context=f"Found {len(matches)} sections mentioning '{query}'"
    )

def save_conversation_context(topic: str, content: str) -> ConversationContext:
    """Save the context of the conversation for later reference."""
    timestamp = datetime.now().isoformat()
    return ConversationContext(
        topic=topic,
        content=content,
        timestamp=timestamp
    )