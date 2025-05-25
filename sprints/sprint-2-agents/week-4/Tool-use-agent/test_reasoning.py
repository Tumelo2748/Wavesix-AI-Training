#!/usr/bin/env python3
"""
Test script to demonstrate the reasoning functionality
without requiring an OpenAI API key.
"""

from core.reasoning import ReasoningTracker, ReasoningAnalyzer
import json

def test_reasoning_tracker():
    """Test the reasoning tracker functionality."""
    print("🧠 Testing Reasoning Tracker")
    print("=" * 50)
    
    # Initialize reasoning tracker
    tracker = ReasoningTracker()
    
    # Simulate a contract analysis process
    tracker.add_reasoning_step(
        "observation", 
        "Received contract analysis request for service agreement",
        confidence=1.0
    )
    
    tracker.add_reasoning_step(
        "thought", 
        "Need to extract and analyze key clauses first to understand contract structure",
        confidence=0.9
    )
    
    tracker.add_reasoning_step(
        "action", 
        "Using extract_clauses tool to identify contract sections",
        tool_used="extract_clauses",
        confidence=0.8
    )
    
    tracker.add_reasoning_step(
        "observation", 
        "Found 12 clauses including payment terms, liability, and termination provisions",
        tool_used="extract_clauses",
        tool_result={"clause_count": 12, "types": ["payment", "liability", "termination"]},
        confidence=1.0
    )
    
    tracker.add_reasoning_step(
        "thought", 
        "Payment clause mentions 'unlimited liability' which could be a significant risk",
        confidence=0.85
    )
    
    tracker.add_reasoning_step(
        "action", 
        "Using flag_for_review tool to flag the liability clause",
        tool_used="flag_for_review",
        confidence=0.9
    )
    
    tracker.add_reasoning_step(
        "thought", 
        "Based on analysis, this appears to be a standard service agreement with one high-risk clause. Overall assessment: proceed with caution on liability terms.",
        confidence=0.8
    )
    
    # Add some decisions
    tracker.add_decision(
        decision="Flag liability clause for legal review",
        reasoning="Clause contains 'unlimited liability' language which poses significant financial risk",
        alternatives=["Accept as-is", "Negotiate liability cap", "Add insurance requirement"],
        evidence=["Clause text mentions unlimited liability", "Industry standard is capped liability"],
        confidence=0.9,
        risk_assessment="High financial risk if liability events occur"
    )
    
    tracker.add_decision(
        decision="Recommend contract acceptance with modifications",
        reasoning="Contract is generally standard but requires liability clause modification",
        alternatives=["Reject entirely", "Accept as-is", "Request multiple changes"],
        evidence=["Standard payment terms", "Reasonable termination clause", "Clear scope of work"],
        confidence=0.75,
        risk_assessment="Medium risk with liability modification, low risk otherwise"
    )
    
    # Display reasoning summary
    print(tracker.get_reasoning_summary())
    print(tracker.get_decisions_summary())
    
    # Export reasoning trace
    trace_data = tracker.export_reasoning_trace()
    print(f"\n📊 Exported trace contains:")
    print(f"   - {trace_data['total_steps']} reasoning steps")
    print(f"   - {trace_data['total_decisions']} decisions")
    print(f"   - Session ID: {trace_data['session_id']}")

def test_reasoning_analyzer():
    """Test the reasoning analyzer functionality."""
    print("\n\n🔍 Testing Reasoning Analyzer")
    print("=" * 50)
    
    # Test clause analysis
    sample_clause = """
    The Service Provider shall indemnify and hold harmless the Client from any and all claims, 
    damages, losses, costs, and expenses (including reasonable attorneys' fees) arising out of 
    or resulting from the Service Provider's negligent or wrongful acts or omissions in the 
    performance of this Agreement. This indemnification shall survive termination of this Agreement.
    """
    
    analysis = ReasoningAnalyzer.analyze_clause_reasoning(sample_clause)
    
    print("📋 Clause Analysis Results:")
    print(f"   - Length: {analysis['clause_length']} characters")
    print(f"   - Clarity Score: {analysis['clarity_score']:.1f}/100")
    print(f"   - Recommendation: {analysis['recommendation']}")
    
    if analysis['complexity_indicators']:
        print("   - Complexity Indicators:")
        for indicator in analysis['complexity_indicators']:
            print(f"     • {indicator}")
    
    if analysis['risk_signals']:
        print("   - Risk Signals Found:")
        for signal in analysis['risk_signals']:
            print(f"     ⚠️ {signal}")
    
    # Test contract analysis strategy
    sample_contract = """
    EMPLOYMENT AGREEMENT
    
    This Employment Agreement is entered into between Company ABC and Employee John Doe.
    The employee agrees to work full-time in the position of Software Developer.
    
    Compensation: $75,000 annually plus benefits.
    Termination: Either party may terminate with 30 days notice.
    Confidentiality: Employee agrees to maintain strict confidentiality of company information.
    Non-compete: Employee agrees not to work for competitors for 1 year after termination.
    """
    
    strategy = ReasoningAnalyzer.suggest_analysis_strategy(sample_contract)
    
    print(f"\n📈 Analysis Strategy:")
    print(f"   - Document Type: {strategy['document_type']}")
    print(f"   - Estimated Complexity: {strategy['estimated_complexity']}")
    print("   - Priority Areas:")
    for area in strategy['priority_areas']:
        print(f"     • {area}")
    print("   - Suggested Analysis Order:")
    for i, step in enumerate(strategy['analysis_order'], 1):
        print(f"     {i}. {step}")
    print("   - Strategy Reasoning:")
    for reason in strategy['reasoning']:
        print(f"     • {reason}")

if __name__ == "__main__":
    print("🤖 Legal Contract Analysis Agent - Reasoning System Test")
    print("=" * 80)
    print("This test demonstrates the enhanced reasoning capabilities")
    print("that have been added to the legal contract analysis agent.\n")
    
    test_reasoning_tracker()
    test_reasoning_analyzer()
    
    print("\n✅ All reasoning tests completed successfully!")
    print("\nThe enhanced agent now provides:")
    print("• Step-by-step reasoning traces")
    print("• Decision tracking with alternatives and evidence") 
    print("• Confidence scoring for analysis steps")
    print("• Risk assessment for flagged clauses")
    print("• Exportable reasoning data for audit trails")
    print("• Analysis strategy suggestions based on document type")
