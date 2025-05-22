import os
from openai import OpenAI

# OpenAI Client Configuration
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Model Configuration
DEFAULT_MODEL = "gpt-4o"  # Using a more capable model for complex legal analysis
MAX_REASONING_STEPS = 10

# System Message
LEGAL_ASSISTANT_SYSTEM_MESSAGE = """You are an advanced legal contract analysis assistant. 
Your capabilities include:
1. Reading and interpreting contract documents from PDFs
2. Extracting key clauses and terms from legal documents
3. Translating legal jargon into simple, clear language
4. Identifying potential risks and hidden meanings in contract provisions
5. Providing detailed summaries of contracts
6. Engaging in conversational discussion about any aspect of the contract

You provide thoughtful analysis of legal documents in a user-friendly, conversational manner.
When answering questions, provide clear explanations and cite specific sections from the contract.
For risky clauses, explain the implications and potential concerns clearly."""

# Tool Configuration
tools = [
    {
        "type": "function",
        "function": {
            "name": "extract_clauses",
            "description": "Extract clauses from a legal text",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "classify_clause",
            "description": "Classify a legal clause by type and risk",
            "parameters": {
                "type": "object",
                "properties": {
                    "clause": {"type": "string"}
                },
                "required": ["clause"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "flag_for_review",
            "description": "Flag a clause as risky",
            "parameters": {
                "type": "object",
                "properties": {
                    "clause": {"type": "string"},
                    "reason": {"type": "string"}
                },
                "required": ["clause", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_pdf",
            "description": "Extract text from a PDF file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"}
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_document",
            "description": "Generate a summary of a legal document",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "max_length": {"type": "integer"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "explain_clause",
            "description": "Explain a legal clause in simple terms",
            "parameters": {
                "type": "object",
                "properties": {
                    "clause": {"type": "string"}
                },
                "required": ["clause"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_document",
            "description": "Search for specific terms or topics in the document",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "query": {"type": "string"}
                },
                "required": ["text", "query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_conversation_context",
            "description": "Save the context of the current conversation for later reference",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["topic", "content"]
            }
        }
    }
]