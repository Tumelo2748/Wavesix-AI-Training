"""
Reasoning module for the legal assistant agent.
Provides structured reasoning capabilities and decision tracking.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class ReasoningStep:
    """Represents a single step in the reasoning process."""
    step_number: int
    action_type: str  # 'observation', 'thought', 'action', 'decision'
    content: str
    tool_used: Optional[str] = None
    tool_result: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class DecisionContext:
    """Context for a specific decision made by the agent."""
    decision: str
    reasoning: str
    alternatives_considered: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    risk_assessment: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

class ReasoningTracker:
    """Tracks and manages the agent's reasoning process."""
    
    def __init__(self):
        self.reasoning_steps: List[ReasoningStep] = []
        self.decisions: List[DecisionContext] = []
        self.current_step = 0
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def add_reasoning_step(self, action_type: str, content: str, 
                          tool_used: Optional[str] = None, 
                          tool_result: Optional[Dict[str, Any]] = None,
                          confidence: Optional[float] = None):
        """Add a reasoning step to the tracker."""
        self.current_step += 1
        step = ReasoningStep(
            step_number=self.current_step,
            action_type=action_type,
            content=content,
            tool_used=tool_used,
            tool_result=tool_result,
            confidence=confidence
        )
        self.reasoning_steps.append(step)
        return step
    
    def add_decision(self, decision: str, reasoning: str, 
                    alternatives: List[str] = None,
                    evidence: List[str] = None,
                    confidence: float = 0.0,
                    risk_assessment: str = ""):
        """Record a decision made by the agent."""
        decision_context = DecisionContext(
            decision=decision,
            reasoning=reasoning,
            alternatives_considered=alternatives or [],
            evidence=evidence or [],
            confidence_score=confidence,
            risk_assessment=risk_assessment
        )
        self.decisions.append(decision_context)
        return decision_context
    
    def get_reasoning_summary(self) -> str:
        """Generate a summary of the reasoning process."""
        if not self.reasoning_steps:
            return "No reasoning steps recorded."
        
        summary = f"🧠 Reasoning Process Summary ({len(self.reasoning_steps)} steps)\n"
        summary += "=" * 50 + "\n\n"
        
        for step in self.reasoning_steps:
            summary += f"Step {step.step_number}: {step.action_type.upper()}\n"
            summary += f"📝 {step.content}\n"
            
            if step.tool_used:
                summary += f"🛠️ Tool: {step.tool_used}\n"
            
            if step.confidence:
                summary += f"🎯 Confidence: {step.confidence:.1%}\n"
            
            summary += "\n"
        
        return summary
    
    def get_decisions_summary(self) -> str:
        """Generate a summary of decisions made."""
        if not self.decisions:
            return "No decisions recorded."
        
        summary = f"⚖️ Decisions Made ({len(self.decisions)} decisions)\n"
        summary += "=" * 40 + "\n\n"
        
        for i, decision in enumerate(self.decisions, 1):
            summary += f"Decision {i}: {decision.decision}\n"
            summary += f"📋 Reasoning: {decision.reasoning}\n"
            summary += f"🎯 Confidence: {decision.confidence_score:.1%}\n"
            
            if decision.alternatives_considered:
                summary += f"🔄 Alternatives: {', '.join(decision.alternatives_considered)}\n"
            
            if decision.evidence:
                summary += f"📊 Evidence: {'; '.join(decision.evidence)}\n"
            
            if decision.risk_assessment:
                summary += f"⚠️ Risk: {decision.risk_assessment}\n"
            
            summary += "\n"
        
        return summary
    
    def export_reasoning_trace(self) -> Dict[str, Any]:
        """Export the complete reasoning trace for analysis."""
        return {
            "session_id": self.session_id,
            "total_steps": len(self.reasoning_steps),
            "total_decisions": len(self.decisions),
            "reasoning_steps": [
                {
                    "step": step.step_number,
                    "action_type": step.action_type,
                    "content": step.content,
                    "tool_used": step.tool_used,
                    "confidence": step.confidence,
                    "timestamp": step.timestamp.isoformat()
                }
                for step in self.reasoning_steps
            ],
            "decisions": [
                {
                    "decision": decision.decision,
                    "reasoning": decision.reasoning,
                    "alternatives": decision.alternatives_considered,
                    "evidence": decision.evidence,
                    "confidence": decision.confidence_score,
                    "risk_assessment": decision.risk_assessment,
                    "timestamp": decision.timestamp.isoformat()
                }
                for decision in self.decisions
            ]
        }

class ReasoningAnalyzer:
    """Analyzes contract content and provides reasoning for analysis decisions."""
    
    @staticmethod
    def analyze_clause_reasoning(clause: str) -> Dict[str, Any]:
        """Provide reasoning analysis for a specific clause."""
        reasoning = {
            "clause_length": len(clause),
            "complexity_indicators": [],
            "risk_signals": [],
            "clarity_score": 0.0,
            "recommendation": ""
        }
        
        # Analyze complexity
        if len(clause) > 500:
            reasoning["complexity_indicators"].append("Very long clause - may be difficult to understand")
        
        # Look for risk signals
        risk_keywords = [
            "unlimited liability", "sole discretion", "without notice",
            "as-is", "no warranty", "indemnify", "hold harmless",
            "liquidated damages", "termination", "breach"
        ]
        
        for keyword in risk_keywords:
            if keyword.lower() in clause.lower():
                reasoning["risk_signals"].append(f"Contains '{keyword}' - potential risk indicator")
        
        # Calculate clarity score (simplified)
        avg_word_length = sum(len(word) for word in clause.split()) / len(clause.split())
        sentence_count = clause.count('.') + clause.count('!') + clause.count('?')
        avg_sentence_length = len(clause.split()) / max(sentence_count, 1)
        
        # Lower score for longer words and sentences (harder to read)
        reasoning["clarity_score"] = max(0, 100 - (avg_word_length * 2) - (avg_sentence_length * 0.5))
        
        # Generate recommendation
        if reasoning["risk_signals"]:
            reasoning["recommendation"] = "Requires careful review due to identified risk signals"
        elif reasoning["clarity_score"] < 50:
            reasoning["recommendation"] = "Consider requesting clearer language"
        else:
            reasoning["recommendation"] = "Appears to be standard contract language"
        
        return reasoning
    
    @staticmethod
    def suggest_analysis_strategy(contract_text: str) -> Dict[str, Any]:
        """Suggest an analysis strategy based on contract characteristics."""
        strategy = {
            "document_type": "unknown",
            "priority_areas": [],
            "analysis_order": [],
            "estimated_complexity": "medium",
            "reasoning": []
        }
        
        text_lower = contract_text.lower()
        
        # Determine document type
        if "employment" in text_lower or "employee" in text_lower:
            strategy["document_type"] = "employment_agreement"
            strategy["priority_areas"] = ["termination", "compensation", "confidentiality", "non-compete"]
        elif "service" in text_lower and "agreement" in text_lower:
            strategy["document_type"] = "service_agreement"
            strategy["priority_areas"] = ["scope of work", "payment terms", "liability", "termination"]
        elif "lease" in text_lower or "rental" in text_lower:
            strategy["document_type"] = "lease_agreement"
            strategy["priority_areas"] = ["rent", "term", "security deposit", "maintenance"]
        elif "purchase" in text_lower or "sale" in text_lower:
            strategy["document_type"] = "purchase_agreement"
            strategy["priority_areas"] = ["price", "delivery", "warranties", "returns"]
        
        # Estimate complexity
        if len(contract_text) > 10000:
            strategy["estimated_complexity"] = "high"
            strategy["reasoning"].append("Long document suggests high complexity")
        elif len(contract_text) < 2000:
            strategy["estimated_complexity"] = "low"
            strategy["reasoning"].append("Short document suggests lower complexity")
        
        # Suggest analysis order
        strategy["analysis_order"] = [
            "Extract key clauses",
            "Classify clauses by type",
            "Identify high-risk provisions",
            "Generate summary",
            "Flag items for review"
        ]
        
        return strategy
