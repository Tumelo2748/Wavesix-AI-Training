"""
Explanation tools for the legal assistant agent.
"""

def explain_clause(clause: str) -> str:
    """Explain a legal clause in simple terms."""
    # In a real implementation, this would use the LLM to explain the clause
    # This is a simplified placeholder
    explanation = "This clause means: "
    
    lc = clause.lower()
    if "data" in lc:
        explanation += "The company can collect and use your personal information as described."
    elif "terminate" in lc:
        explanation += "The company can end your service at any time for any reason."
    elif "jurisdiction" in lc:
        explanation += "Any legal disputes will be handled according to the laws of the specified location."
    elif "liability" in lc:
        explanation += "The company is limiting how much they can be held responsible for problems or damages."
    else:
        explanation += "This establishes standard terms for the agreement between parties."
        
    return explanation