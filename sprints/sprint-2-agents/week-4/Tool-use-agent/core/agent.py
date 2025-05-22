"""
Core agent functionality for the legal assistant.
"""
import json
from typing import List, Dict, Any
import os

# Import LLM Configuration
from config.llm_config import client, tools, DEFAULT_MODEL, MAX_REASONING_STEPS, LEGAL_ASSISTANT_SYSTEM_MESSAGE

# Import tool functions
from tools.analysis_tools import classify_clause, flag_for_review
from tools.document_tools import extract_clauses, read_pdf, summarize_document
from tools.explanation_tools import explain_clause
from tools.search_tools import search_document, save_conversation_context

# -------------------------
# Function Router
# -------------------------

def call_function(name: str, arguments: str):
    """Route function calls to the appropriate tool function."""
    data = json.loads(arguments)
    if name == "extract_clauses":
        return extract_clauses(**data).model_dump()
    elif name == "classify_clause":
        return classify_clause(**data).model_dump()
    elif name == "flag_for_review":
        return flag_for_review(**data).model_dump()
    elif name == "read_pdf":
        return read_pdf(**data)
    elif name == "summarize_document":
        return summarize_document(**data).model_dump()
    elif name == "explain_clause":
        return explain_clause(**data)
    elif name == "search_document":
        return search_document(**data).model_dump()
    elif name == "save_conversation_context":
        return save_conversation_context(**data).model_dump()
    else:
        raise ValueError(f"Unknown function: {name}")

# -------------------------
# ReAct Agent Loop
# -------------------------

def run_agent(input_text: str):
    """Run the agent with a new input text."""
    messages = [
        {"role": "system", "content": LEGAL_ASSISTANT_SYSTEM_MESSAGE},
        {"role": "user", "content": input_text}
    ]

    flagged = []
    
    for _ in range(MAX_REASONING_STEPS):  # max reasoning steps
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        msg = response.choices[0].message
        
        # Handle assistant message
        if msg.tool_calls:
            # For messages with tool calls, don't include content if it's None
            messages.append({
                "role": msg.role,
                **({"content": msg.content} if msg.content is not None else {}),
                "tool_calls": msg.tool_calls
            })
            
            # Process each tool call
            for tool_call in msg.tool_calls:
                tool_name = tool_call.function.name
                tool_args = tool_call.function.arguments
                print(f"\n🛠 Tool call: {tool_name}()")
                result = call_function(tool_name, tool_args)

                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(result)
                })

                if tool_name == "flag_for_review":
                    flagged.append(json.loads(json.dumps(result)))
        else:
            # For regular messages, always include content
            messages.append({"role": msg.role, "content": msg.content or ""})
            print("\n✅ Final Answer:")
            print(msg.content)
            break

    if flagged:
        print("\n🚩 Flagged Clauses:")
        for f in flagged:
            print(f"- {f['reason']}\n  → {f['clause'][:80]}...\n")
    return messages

def run_agent_with_history(messages):
    """Run the agent with an existing conversation history."""
    flagged = []
    
    for _ in range(MAX_REASONING_STEPS):
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        msg = response.choices[0].message
        
        # Handle assistant message
        if msg.tool_calls:
            # For messages with tool calls, don't include content if it's None
            messages.append({
                "role": msg.role,
                **({"content": msg.content} if msg.content is not None else {}),
                "tool_calls": msg.tool_calls
            })
            
            # Process each tool call
            for tool_call in msg.tool_calls:
                tool_name = tool_call.function.name
                tool_args = tool_call.function.arguments
                print(f"\n🛠 Tool call: {tool_name}()")
                result = call_function(tool_name, tool_args)

                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(result)
                })

                if tool_name == "flag_for_review":
                    flagged.append(json.loads(json.dumps(result)))
        else:
            # For regular messages, always include content
            messages.append({"role": msg.role, "content": msg.content or ""})
            print("\n🤖 Assistant: ")
            print(msg.content)
            break

    if flagged:
        print("\n🚩 Flagged Clauses:")
        for f in flagged:
            print(f"- {f['reason']}\n  → {f['clause'][:80]}...\n")
    
    return messages

def list_available_contracts():
    """List all PDF contracts in the docs/contracts folder."""
    contracts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "contracts")
    if not os.path.exists(contracts_dir):
        return []
    
    contracts = [f for f in os.listdir(contracts_dir) if f.lower().endswith(('.pdf', '.txt'))]
    return contracts