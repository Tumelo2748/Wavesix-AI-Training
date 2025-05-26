"""
Core agent functionality for the legal assistant.
"""
import json
from typing import List, Dict, Any
import os
from openai import OpenAI

# Import LLM Configuration
from config.llm_config import client, tools, DEFAULT_MODEL

def run_agent(input_text: str):
    """
    Run the agent with the provided input text.
    """
    