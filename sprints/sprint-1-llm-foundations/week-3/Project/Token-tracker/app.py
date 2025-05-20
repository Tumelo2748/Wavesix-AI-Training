# Example usage of the TokenTracker library
from token_tracker import TokenTracker
import json
import os

def main():
    """
    Example of using the TokenTracker to monitor token usage
    """
    # Create a logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Initialize token tracker with GPT-4 model and log path
    tracker = TokenTracker(
        model_name="gpt-4-turbo", 
        log_path="logs/token_usage.jsonl"
    )
    
    # Example 1: Simple token counting and cost calculation
    prompt = "Tell me about the history of artificial intelligence."
    completion = """Artificial intelligence (AI) has a rich history dating back to the mid-20th century. 
    The term "artificial intelligence" was coined in 1956 at the Dartmouth Conference, which is widely 
    considered the founding event of AI as a field. Early AI research focused on symbolic approaches 
    and rule-based systems.
    
    In the 1980s, AI experienced what is known as the "AI winter," a period of reduced funding and interest
    due to unmet expectations. However, the field revived in the 1990s with new approaches focusing on 
    statistical methods and machine learning.
    
    The 2010s saw a significant breakthrough with the rise of deep learning, enabled by increased 
    computational power and large datasets. This led to remarkable advances in areas like computer vision,
    natural language processing, and game playing.
    
    Today, AI has become ubiquitous, powering everything from virtual assistants and recommendation 
    systems to autonomous vehicles and medical diagnosis tools. The field continues to evolve rapidly, 
    with ongoing research in areas like reinforcement learning, generative models, and multi-modal systems."""
    
    # Log the interaction
    interaction = tracker.log_interaction(prompt, completion)
    
    # Print token usage and cost for this interaction
    print("Example 1: Simple Query")
    print(f"Prompt tokens: {interaction['tokens']['prompt']}")
    print(f"Completion tokens: {interaction['tokens']['completion']}")
    print(f"Total tokens: {interaction['tokens']['total']}")
    print(f"Cost: ${interaction['cost']['total']:.6f}")
    print("-" * 50)
    
    # Example 2: Another interaction with metadata
    prompt = "What are the key considerations for implementing ethical AI systems?"
    completion = """Implementing ethical AI systems requires careful consideration of several key principles:
    
    1. Fairness and Bias Mitigation: Ensure AI systems treat all individuals fairly without discriminating 
       based on protected attributes like race, gender, or age.
    
    2. Transparency and Explainability: AI systems should be transparent about their operation and capable of 
       providing explanations for their decisions that humans can understand.
    
    3. Privacy and Data Protection: Respect user privacy by implementing strong data protection measures and 
       ensuring informed consent for data collection and use.
    
    4. Safety and Robustness: Build AI systems that operate safely, reliably, and as intended, even when 
       faced with unexpected inputs or adversarial attacks.
    
    5. Accountability: Establish clear lines of responsibility for AI system outcomes and create mechanisms 
       to address adverse effects.
    
    6. Human Oversight: Maintain appropriate human control and oversight, especially for high-risk AI applications.
    
    7. Social and Environmental Impact: Consider the broader societal and environmental implications of AI deployment.
    
    8. Inclusive Design: Involve diverse stakeholders in the design process to ensure AI benefits all segments of society.
    
    Implementing these considerations often requires cross-disciplinary collaboration, ongoing monitoring and 
    evaluation, and adaptive governance frameworks that can evolve with advancing technology."""
    
    # Log the interaction with metadata
    interaction = tracker.log_interaction(
        prompt, 
        completion,
        metadata={
            "project": "ethics_guidelines",
            "user_id": "example_user_123",
            "purpose": "educational"
        }
    )
    
    # Print token usage and cost for this interaction
    print("Example 2: Query with Metadata")
    print(f"Prompt tokens: {interaction['tokens']['prompt']}")
    print(f"Completion tokens: {interaction['tokens']['completion']}")
    print(f"Total tokens: {interaction['tokens']['total']}")
    print(f"Cost: ${interaction['cost']['total']:.6f}")
    print(f"Metadata: {json.dumps(interaction['metadata'], indent=2)}")
    print("-" * 50)
    
    # Get session summary
    summary = tracker.get_session_summary()
    print("Session Summary:")
    print(f"Total tokens used: {summary['tokens']['total']}")
    print(f"Total cost: ${summary['cost']:.6f}")
    print(f"Number of interactions: {summary['interactions_count']}")
    
    # Export session data to a JSON file
    export_path = tracker.export_session_data("logs/session_export.json")
    print(f"Session data exported to: {export_path}")

if __name__ == "__main__":
    main()