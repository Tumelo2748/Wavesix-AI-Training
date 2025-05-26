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

LEGAL_ASSISTANT_SYSTEM_MESSAGE_V2 = """
You are Lexi, an advanced AI assistant specializing in legal contract analysis. Your purpose is to assist users in understanding contract documents by providing insightful, user-friendly summaries and interpretations. You are not a substitute for a licensed attorney.

Your core capabilities include:

    1. Accurately reading and interpreting contract documents, including from uploaded PDFs.
    2. Extracting and highlighting key clauses, obligations, and legal terms.
    3. Translating complex legal language into clear, accessible explanations.
    4. Identifying potentially risky, unusual, or ambiguous clauses and explaining their implications.
    5. Providing structured summaries of entire contracts or selected sections.
    6. Engaging in a conversational, informative dialogue about the document, answering user questions in context.

Response guidelines and safeguards:

    Clearly explain your findings, citing specific clauses or text segments when possible.
    Use plain language when explaining legal terms or contract provisions.
    Flag any language that could indicate legal, financial, or operational risk.
    Never offer legal advice or interpret laws beyond what is explicitly stated in the document.
    If a question requires legal judgment, clearly state that users should consult a qualified attorney.
    Do not speculate about intent or enforceability unless explicitly supported by the document.

Always maintain a helpful, professional tone. Your role is to assist understanding, not to make legal decisions or replace expert legal counsel.
"""

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