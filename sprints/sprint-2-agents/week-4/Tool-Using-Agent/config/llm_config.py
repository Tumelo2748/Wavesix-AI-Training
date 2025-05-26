import os
from openai import OpenAI

# OpenAI Client Configuration
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Model Configuration
DEFAULT_MODEL = "gpt-3.5"

System_prompt_v0 = """
    
"""