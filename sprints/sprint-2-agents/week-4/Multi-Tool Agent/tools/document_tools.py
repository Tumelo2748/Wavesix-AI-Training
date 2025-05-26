"""
Document processing tools for the legal assistant agent.
"""
import PyPDF2
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Import models from the models module
from models.data_models import Clause, ClauseExtractionOutput, DocumentSummary

def extract_clauses(text: str) -> ClauseExtractionOutput:
    """Extract clauses from a legal text."""
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    return ClauseExtractionOutput(
        clauses=[Clause(text=p, start_idx=i, end_idx=i+len(p)) for i, p in enumerate(parts)]
    )

def read_pdf(file_path: str) -> str:
    """Extract text from a PDF file or read text file."""
    try:
        # If it's a text file, read it directly
        if file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        # Otherwise, try to read it as a PDF
        else:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n\n"
                return text
    except Exception as e:
        return f"Error reading file: {str(e)}"

def summarize_document(text: str, max_length: int = 500) -> DocumentSummary:
    """Generate a summary of a legal document."""
    # Using a text splitter to break the document into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=20,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = text_splitter.split_text(text)
    
    key_points = []
    risks = []
    
    for i, chunk in enumerate(chunks[:5]):  # Just use first 5 chunks for example
        lc = chunk.lower()
        if "data" in lc or "privacy" in lc:
            risks.append({"clause": chunk[:100] + "...", "reason": "Privacy concerns"})
        elif "terminate" in lc:
            risks.append({"clause": chunk[:100] + "...", "reason": "Termination rights"})
        elif "liability" in lc:
            risks.append({"clause": chunk[:100] + "...", "reason": "Liability limitations"})
        
        if i < 3:  # Add first 3 chunks as key points
            key_points.append(f"Section {i+1}: {chunk[:50]}...")
    
    return DocumentSummary(
        overview=f"This document contains {len(chunks)} sections covering various legal aspects.",
        key_points=key_points,
        risks=risks
    )