# Legal Contract Analysis Assistant

A tool-use agent for analyzing legal contracts with AI assistance.

## Overview

This application leverages AI to help users analyze legal contracts, identify potential risks, and understand complex legal terminology. The assistant provides a conversational interface that allows users to:

- Extract and interpret key terms, conditions, and clauses in simple language
- Identify hidden meanings, implications, and potential risks
- Engage in interactive conversations about any part of the contract
- Get detailed summaries and highlights of important sections

## Features

- **PDF and Text File Support**: Analyze contracts in PDF or TXT format
- **Clause Extraction**: Automatically identify and extract key clauses
- **Risk Assessment**: Flag high-risk clauses with explanations
- **Plain Language Explanations**: Translate legal jargon into simple terms
- **Interactive Search**: Find specific terms or concepts within contracts
- **Document Summarization**: Get concise summaries of lengthy contracts
- **Conversation History**: Maintain context throughout the conversation

## Setup

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Installation

1. Clone this repository or download the source code

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv env
   # On Windows
   env\Scripts\activate
   # On macOS/Linux
   source env/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install openai pydantic langchain PyPDF2
   ```

4. Set your OpenAI API key as an environment variable:
   ```bash
   # On Windows
   export OPENAI_API_KEY=****************************
   # On macOS/Linux
   export OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Run the application:
   ```bash
   python app.py
   ```

2. Use the following commands in the interactive shell:
   - `help` - Show available commands
   - `list` - List available contracts in the docs/contracts folder
   - `open <contract_name>` - Open and analyze a specific contract (can use the number from the list)
   - `summary` - Get a summary of the current contract
   - `search <term>` - Search for a specific term in the current contract
   - `explain <clause>` - Explain a specific clause in simple terms
   - `exit` or `quit` - Exit the application

3. Adding contracts:
   - Place your PDF or TXT contracts in the `docs/contracts` folder
   - They will automatically appear when you use the `list` command

## Example Session

```
🤖 Legal Contract Analysis Assistant
======================================
I can help analyze legal contracts from PDF files.
Type 'help' to see available commands or 'exit' to quit.

📚 Available Commands:
---------------------
help                    - Show this help message
list                    - List available contracts in the docs/contracts folder
open <contract_name>    - Open and analyze a specific contract
summary                 - Get a summary of the current contract
search <term>           - Search for a specific term in the current contract
explain <clause>        - Explain a specific clause in simple terms
exit, quit              - Exit the application

You can also ask questions in natural language about the contract.

📝 You: list

📄 Available Contracts:
  1. sample_service_agreement.txt

Type 'open <contract_name>' to analyze a contract.

📝 You: open 1

📄 Reading contract: sample_service_agreement.txt

🛠 Tool call: extract_clauses()
🛠 Tool call: classify_clause()
🛠 Tool call: summarize_document()

✅ Final Answer:
I've analyzed the Sample Service Agreement. Here's a summary:

This is a service agreement between Don't Play Corporation and a Client, outlining the terms for services described in Schedule A. Key points include:

1. Services will be performed according to professional standards
2. The agreement can be terminated with 30 days' notice by the Client
3. Either party can terminate immediately for material breach
4. Payment terms include monthly invoicing with 30-day payment period
5. Contains confidentiality and data privacy provisions
6. Includes intellectual property rights allocation
7. Has liability limitations and disclaimers of warranties
8. Uses California law for governance and arbitration for disputes

High-risk clauses include the termination provisions, liability limitations, and data collection clauses. Would you like me to explain any specific section in more detail?

📝 You: explain the data privacy section

🤖 Assistant:
The data privacy section (Section 5) outlines how the company handles client data. Here's a simplified explanation:

5.1 Data Collection: The company collects data from the client and its users, including personal information, device identifiers, and usage patterns. This allows them to provide the contracted services.

5.2 Data Use: The company can use this collected data for three primary purposes:
   - Improving their services
   - Providing customer support
   - Analyzing usage patterns

Importantly, the company states they will not sell or rent the client's data to third parties without explicit consent from the client. This is a positive privacy protection.

5.3 Data Security: The company commits to implementing "reasonable" technical and organizational measures to protect the client's data from unauthorized access, disclosure, or destruction.

Key considerations about this section:
- The term "reasonable" for security measures is somewhat vague and provides flexibility for the company
- While the company won't sell data without consent, they can still use it internally for various purposes
- There's no specific mention of data retention periods or deletion policies
- The clause doesn't specify what happens to data if the agreement terminates

This is a moderate-risk section because while it provides some protections, it still gives the company significant latitude in how they handle your data.
```

## System Architecture

- `app.py`: Main application with the CLI interface and agent implementation
- `llm_config.py`: Configuration for the LLM (model, system prompt, tools)
- `docs/contracts/`: Folder containing contract files for analysis

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Built with OpenAI's API
- Uses LangChain for text processing
- PyPDF2 for PDF file handling