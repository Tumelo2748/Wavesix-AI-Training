"""
Core agent functionality for the legal assistant.
"""
import json
from typing import List, Dict, Any
import os

# Import LLM Configuration
from config.llm_config import client, tools, DEFAULT_MODEL, MAX_REASONING_STEPS, LEGAL_ASSISTANT_SYSTEM_MESSAGE, LEGAL_ASSISTANT_SYSTEM_MESSAGE_V2

# Import tool functions
from tools.analysis_tools import classify_clause, flag_for_review
from tools.document_tools import extract_clauses, read_pdf, summarize_document
from tools.explanation_tools import explain_clause
from tools.search_tools import search_document, save_conversation_context

# Import reasoning capabilities
from core.reasoning import ReasoningTracker, ReasoningAnalyzer

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
    """Run the agent with a new input text and reasoning tracking."""
    # Initialize reasoning tracker
    reasoning_tracker = ReasoningTracker()
    
    # Add initial reasoning step
    reasoning_tracker.add_reasoning_step(
        "observation", 
        f"Received user input: {input_text[:100]}..." if len(input_text) > 100 else f"Received user input: {input_text}",
        confidence=1.0
    )
    
    # Enhanced system message that includes reasoning requirements
    enhanced_system_message = LEGAL_ASSISTANT_SYSTEM_MESSAGE_V2 + """

REASONING REQUIREMENTS:
- Always explain your thought process step by step
- When using tools, explain why you chose that specific tool
- When making decisions, consider alternatives and explain your choice
- Provide confidence levels for your analysis
- Flag any assumptions you're making
- Explain the reasoning behind flagging clauses for review
"""
    
    messages = [
        {"role": "system", "content": enhanced_system_message},
        {"role": "user", "content": input_text}
    ]

    flagged = []
    
    for iteration in range(MAX_REASONING_STEPS):  # max reasoning steps
        reasoning_tracker.add_reasoning_step(
            "thought", 
            f"Starting reasoning iteration {iteration + 1}",
            confidence=0.8
        )
        
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        msg = response.choices[0].message
        
        # Track the assistant's reasoning
        if msg.content:
            reasoning_tracker.add_reasoning_step(
                "thought", 
                msg.content,
                confidence=0.9
            )
        
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
                
                # Track tool usage reasoning
                reasoning_tracker.add_reasoning_step(
                    "action", 
                    f"Using tool {tool_name} to gather information",
                    tool_used=tool_name,
                    confidence=0.8
                )
                
                print(f"\n🛠 Tool call: {tool_name}()")
                result = call_function(tool_name, tool_args)
                
                # Track tool result
                reasoning_tracker.add_reasoning_step(
                    "observation", 
                    f"Tool {tool_name} returned results",
                    tool_used=tool_name,
                    tool_result=result,
                    confidence=1.0
                )

                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(result)
                })

                if tool_name == "flag_for_review":
                    flagged.append(json.loads(json.dumps(result)))
                      # Record flagging decision
                    reasoning_tracker.add_decision(
                        decision=f"Flagged clause for review",
                        reasoning=result.get('reason', 'No specific reason provided'),                        evidence=[f"Clause content: {result.get('clause', '')[:100]}..."],
                        confidence=0.8,
                        risk_assessment=f"Risk level based on: {result.get('reason', 'general concerns')}"
                    )
        else:
            # For regular messages, always include content
            messages.append({"role": msg.role, "content": msg.content or ""})
            
            # Record final decision
            reasoning_tracker.add_decision(
                decision="Completed analysis and provided final response",
                reasoning="Reached conclusion based on document analysis and tool usage",
                confidence=0.9
            )
            
            # Display reasoning summary (which includes the final analysis)
            print("\n" + "="*60)
            print("🧠 REASONING TRACE")
            print("="*60)
            print(reasoning_tracker.get_reasoning_summary())
            
            if reasoning_tracker.decisions:
                print(reasoning_tracker.get_decisions_summary())
            
            break

    if flagged:
        print("\n🚩 Flagged Clauses:")
        for f in flagged:
            print(f"- {f['reason']}\n  → {f['clause'][:80]}...\n")
    
    # Store reasoning tracker for potential export
    messages.append({"role": "system", "content": f"reasoning_tracker_id:{reasoning_tracker.session_id}"})
    
    return messages, reasoning_tracker

def run_agent_with_history(messages):
    """Run the agent with an existing conversation history and reasoning tracking."""
    # Initialize reasoning tracker for this continuation
    reasoning_tracker = ReasoningTracker()
    
    reasoning_tracker.add_reasoning_step(
        "observation", 
        "Continuing conversation with existing history",
        confidence=1.0
    )
    
    flagged = []
    
    for iteration in range(MAX_REASONING_STEPS):
        reasoning_tracker.add_reasoning_step(
            "thought", 
            f"Processing continuation iteration {iteration + 1}",
            confidence=0.8
        )
        
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        msg = response.choices[0].message
        
        # Track the assistant's reasoning
        if msg.content:
            reasoning_tracker.add_reasoning_step(
                "thought", 
                msg.content,
                confidence=0.9
            )
        
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
                
                # Track tool usage reasoning
                reasoning_tracker.add_reasoning_step(
                    "action", 
                    f"Using tool {tool_name} for additional analysis",
                    tool_used=tool_name,
                    confidence=0.8
                )
                
                print(f"\n🛠 Tool call: {tool_name}()")
                result = call_function(tool_name, tool_args)
                
                # Track tool result
                reasoning_tracker.add_reasoning_step(
                    "observation", 
                    f"Tool {tool_name} provided results",
                    tool_used=tool_name,
                    tool_result=result,
                    confidence=1.0
                )

                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(result)
                })

                if tool_name == "flag_for_review":
                    flagged.append(json.loads(json.dumps(result)))
                      # Record flagging decision
                    reasoning_tracker.add_decision(
                        decision=f"Flagged additional clause for review",
                        reasoning=result.get('reason', 'No specific reason provided'),
                        evidence=[f"Clause content: {result.get('clause', '')[:100]}..."],
                        confidence=0.8,
                        risk_assessment=f"Risk identified: {result.get('reason', 'general concerns')}"
                    )
        else:
            # For regular messages, always include content
            messages.append({"role": msg.role, "content": msg.content or ""})
              # Record final decision
            reasoning_tracker.add_decision(
                decision="Provided follow-up response",
                reasoning="Responded to user query based on conversation context",
                confidence=0.9
            )
            
            # Display reasoning summary for this interaction (which includes the response)
            if reasoning_tracker.reasoning_steps:
                print("\n" + "="*50)
                print("🧠 FOLLOW-UP REASONING")
                print("="*50)
                print(reasoning_tracker.get_reasoning_summary())
                
                if reasoning_tracker.decisions:
                    print(reasoning_tracker.get_decisions_summary())
            
            break

    if flagged:
        print("\n🚩 Flagged Clauses:")
        for f in flagged:
            print(f"- {f['reason']}\n  → {f['clause'][:80]}...\n")
    
    return messages, reasoning_tracker

def list_available_contracts():
    """List all PDF contracts in the docs/contracts folder."""
    contracts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "contracts")
    if not os.path.exists(contracts_dir):
        return []
    
    contracts = [f for f in os.listdir(contracts_dir) if f.lower().endswith(('.pdf', '.txt'))]
    return contracts