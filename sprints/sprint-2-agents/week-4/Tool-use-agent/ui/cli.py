"""
Command Line Interface for the Legal Contract Analysis Tool.
"""
import os

# Import agent functions from core module
from core.agent import run_agent, run_agent_with_history, list_available_contracts
from tools.document_tools import read_pdf

def display_help():
    """Display help information about the available commands."""
    print("\n📚 Available Commands:")
    print("---------------------")
    print("help                    - Show this help message")
    print("list                    - List available contracts in the docs/contracts folder")
    print("open <contract_name>    - Open and analyze a specific contract")
    print("summary                 - Get a summary of the current contract")
    print("search <term>           - Search for a specific term in the current contract")
    print("explain <clause>        - Explain a specific clause in simple terms")
    print("exit, quit              - Exit the application")
    print("\nYou can also ask questions in natural language about the contract.")

def run_cli():
    """Run the CLI interface for the Legal Contract Analysis Assistant."""
    print("🤖 Legal Contract Analysis Assistant")
    print("======================================")
    print("I can help analyze legal contracts from PDF files.")
    print("Type 'help' to see available commands or 'exit' to quit.\n")
    
    contract_path = None
    contract_name = None
    contract_text = None
    conversation_messages = []
    
    # Create contracts directory if it doesn't exist
    contracts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "contracts")
    os.makedirs(contracts_dir, exist_ok=True)
    
    display_help()
    
    while True:
        user_input = input("\n📝 You: ")
        
        if user_input.lower() in ['exit', 'quit']:
            print("\nThank you for using the Legal Contract Analysis Assistant. Goodbye!")
            break
        
        elif user_input.lower() == 'help':
            display_help()
            continue
            
        elif user_input.lower() == 'list':
            contracts = list_available_contracts()
            if contracts:
                print("\n📄 Available Contracts:")
                for i, contract in enumerate(contracts, 1):
                    print(f"  {i}. {contract}")
                print("\nType 'open <contract_name>' to analyze a contract.")
            else:
                print("\nNo contracts found in the docs/contracts folder.")
                print("Please add PDF contracts to this folder and try again.")
            continue
            
        elif user_input.lower().startswith('open '):
            # Extract contract name from command
            contract_name = user_input[5:].strip()
            
            # Check if the user provided a number
            if contract_name.isdigit():
                contracts = list_available_contracts()
                index = int(contract_name) - 1
                if 0 <= index < len(contracts):
                    contract_name = contracts[index]
                else:
                    print(f"\n❌ Invalid contract number. Please use a number between 1 and {len(contracts)}.")
                    continue
            # Try to find the contract in the contracts folder
            contract_path = os.path.join(contracts_dir, contract_name)
            
            # If the path doesn't exist and doesn't have a supported extension, try adding .pdf or .txt
            if not os.path.exists(contract_path):
                if not contract_path.lower().endswith(('.pdf', '.txt')):
                    if os.path.exists(contract_path + '.pdf'):
                        contract_path += '.pdf'
                    elif os.path.exists(contract_path + '.txt'):
                        contract_path += '.txt'
                
            if os.path.exists(contract_path):
                print(f"\n📄 Reading contract: {os.path.basename(contract_path)}")
                contract_text = read_pdf(contract_path)
                
                # Reset conversation with the new contract
                conversation_messages = []
                
                # Start analysis with the new contract
                prompt = f"I have uploaded a contract in PDF format called '{os.path.basename(contract_path)}'. Here is the text:\n\n{contract_text[:3000]}...\n\nPlease analyze this contract, extract key clauses, and provide a summary."
                conversation_messages = run_agent(prompt)
                
            else:
                print(f"\n❌ Contract not found: {contract_name}")
                print("Type 'list' to see available contracts.")
            continue
            
        elif user_input.lower() == 'summary':
            if contract_text:
                prompt = f"Please provide a concise summary of the main points in this contract."
                conversation_messages.append({"role": "user", "content": prompt})
                conversation_messages = run_agent_with_history(conversation_messages)
            else:
                print("\n❌ No contract loaded. Use 'open <contract_name>' to load a contract first.")
            continue
            
        elif user_input.lower().startswith('search '):
            if contract_text:
                search_term = user_input[7:].strip()
                prompt = f"Please search the contract for any mentions of '{search_term}' and explain the relevant sections."
                conversation_messages.append({"role": "user", "content": prompt})
                conversation_messages = run_agent_with_history(conversation_messages)
            else:
                print("\n❌ No contract loaded. Use 'open <contract_name>' to load a contract first.")
            continue
            
        elif user_input.lower().startswith('explain '):
            if contract_text:
                clause = user_input[8:].strip()
                prompt = f"Please explain this clause in simple terms: '{clause}'"
                conversation_messages.append({"role": "user", "content": prompt})
                conversation_messages = run_agent_with_history(conversation_messages)
            else:
                print("\n❌ No contract loaded. Use 'open <contract_name>' to load a contract first.")
            continue
        
        # Continue the conversation with previous context
        if conversation_messages:
            # Add the new user message to existing conversation
            conversation_messages.append({"role": "user", "content": user_input})
            conversation_messages = run_agent_with_history(conversation_messages)
        else:
            # First interaction without a contract
            print("\n❓ No contract loaded. Please use 'list' to see available contracts or 'open <contract_name>' to load a contract.")
            display_help()

if __name__ == "__main__":
    run_cli()