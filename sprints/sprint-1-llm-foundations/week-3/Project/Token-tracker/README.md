# TokenTracker

A simple, reusable Python library for tracking token usage and costs in AI projects, particularly when working with language models like GPT-4, GPT-3.5, Claude, and others.

## Features

- Track token usage for prompts and completions
- Calculate costs based on current pricing models
- Log token usage to a file
- Support for metadata to organize interactions
- Session tracking for aggregating statistics
- Export session data to JSON
- Automatic token counting using tiktoken (OpenAI's tokenizer)
- Fallback to approximate counting when tiktoken isn't available

## Installation

```bash
pip install -r requirements.txt
```

## Basic Usage

```python
from token_tracker import TokenTracker

# Initialize token tracker with the model name and optional log path
tracker = TokenTracker(
    model_name="gpt-4-turbo", 
    log_path="logs/token_usage.jsonl"
)

# Log an interaction
prompt = "What is artificial intelligence?"
completion = "Artificial intelligence is the simulation of human intelligence processes by machines..."

interaction = tracker.log_interaction(prompt, completion)

# Print token usage and cost
print(f"Prompt tokens: {interaction['tokens']['prompt']}")
print(f"Completion tokens: {interaction['tokens']['completion']}")
print(f"Total tokens: {interaction['tokens']['total']}")
print(f"Cost: ${interaction['cost']['total']:.6f}")

# Get session summary
summary = tracker.get_session_summary()
print(f"Total tokens used: {summary['tokens']['total']}")
print(f"Total cost: ${summary['cost']:.6f}")
```

## Advanced Usage

### Adding Metadata

```python
tracker.log_interaction(
    prompt, 
    completion,
    metadata={
        "project": "customer_support",
        "user_id": "user123",
        "category": "technical_issue"
    }
)
```

### Updating Pricing for Custom Models

```python
# Update pricing for a model (cost per 1000 tokens)
tracker.update_pricing(
    model_name="custom-model", 
    prompt_price=0.005,  # $0.005 per 1K tokens for prompts
    completion_price=0.008  # $0.008 per 1K tokens for completions
)
```

### Exporting Session Data

```python
# Export all session data to a JSON file
export_path = tracker.export_session_data("logs/session_export.json")
print(f"Session data exported to: {export_path}")
```

### Resetting the Session

```python
# Reset the session counters to start a new tracking session
tracker.reset_session()
```

## Integration with OpenAI API

See `openai_example.py` for a complete example of integrating TokenTracker with the OpenAI API.

## Supported Models (Built-in Pricing)

- gpt-4-turbo
- gpt-4
- gpt-3.5-turbo
- gpt-3.5-turbo-16k
- claude-3-opus
- claude-3-sonnet
- claude-3-haiku
- llama-3-70b

Custom models can be added using the `update_pricing` method.

## License

MIT
