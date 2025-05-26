"""
Analysis tools for the legal assistant agent.
"""
from typing import List, Dict
# Import models from the models module
from models.data_models import ClassificationOutput, FlaggedClause

def classify_clause(clause: str) -> ClassificationOutput:
    """Classify a legal clause by type and risk level."""
    lc = clause.lower()
    if "data" in lc:
        return ClassificationOutput(category="Data Collection", risk_level="medium", summary="Mentions data usage.")
    elif "terminate" in lc:
        return ClassificationOutput(category="Termination", risk_level="high", summary="Unilateral termination.")
    elif "jurisdiction" in lc:
        return ClassificationOutput(category="Jurisdiction", risk_level="medium", summary="Specifies jurisdiction.")
    elif "liability" in lc:
        return ClassificationOutput(category="Liability Limitation", risk_level="high", summary="Limits liability.")
    else:
        return ClassificationOutput(category="Other", risk_level="low", summary="No critical issues detected.")

def flag_for_review(clause: str, reason: str) -> FlaggedClause:
    """Flag a clause as risky for further review."""
    return FlaggedClause(clause=clause, reason=reason)