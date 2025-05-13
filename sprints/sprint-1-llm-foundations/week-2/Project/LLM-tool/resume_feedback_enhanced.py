import os
import argparse
import json
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    try:
        import pdfplumber
        text_content = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
        
        return "\n".join(text_content)
    except ImportError:
        print("Error: pdfplumber is not installed. Install it using: pip install pdfplumber")
        return None
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return None

def generate_resume_feedback(resume_text, role=None):
    """
    Generate feedback for a resume using OpenAI's GPT model.
    
    Args:
        resume_text (str): The resume text to analyze
        role (str, optional): Target job role to tailor feedback for
    
    Returns:
        dict: Structured feedback including strengths, areas for improvement, and suggestions
    """
    if not openai.api_key:
        print("Error: OpenAI API key not found. Please set it in the .env file.")
        return None
        
    # Build the prompt
    role_context = f" for a {role} position" if role else ""
    
    prompt = f"""You are a career coach helping people improve their resumes. Analyze the following resume{role_context} and provide:
1. Summary of strengths (3-5 points)
2. Areas for improvement (3-5 points)
3. Suggested changes to wording or formatting (3-5 specific suggestions)

Resume:
---
{resume_text}

Return your feedback in JSON format with the following structure:
{{
    "strengths": ["strength1", "strength2", ...],
    "areas_for_improvement": ["area1", "area2", ...],
    "suggested_edits": ["suggestion1", "suggestion2", ...]
    
}}
"""
    
    # Call the OpenAI API
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful career coach that gives clear, specific resume feedback."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        # Extract and return the feedback
        feedback = response.choices[0].message.content
        return json.loads(feedback)
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return None

def interactive_mode():
    """Run the tool in interactive mode, asking for user input."""
    print("\n===== Resume Feedback Generator =====")
    print("------------------------------------")
    
    # Get resume input method
    print("\nHow would you like to provide your resume?")
    print("1. Paste text")
    print("2. Load from text file")
    print("3. Load from PDF file")
    
    choice = input("Enter your choice (1-3): ").strip()
    
    resume_text = ""
    
    if choice == "1":
        # Get resume text from user
        print("\nPlease paste your resume text below (type 'DONE' on a new line when finished):")
        resume_lines = []
        while True:
            line = input()
            if line == "DONE":
                break
            resume_lines.append(line)
        resume_text = "\n".join(resume_lines)
    
    elif choice == "2":
        # Get resume from text file
        file_path = input("\nEnter the path to your resume text file: ").strip()
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                resume_text = file.read()
            print(f"Successfully loaded resume from {file_path}")
        except Exception as e:
            print(f"Error loading file: {str(e)}")
            return
    
    elif choice == "3":
        # Get resume from PDF file
        file_path = input("\nEnter the path to your resume PDF file: ").strip()
        resume_text = extract_text_from_pdf(file_path)
        if not resume_text:
            return
        print(f"Successfully loaded resume from {file_path}")
    
    else:
        print("Invalid choice. Exiting.")
        return
    
    # Check if resume text was loaded
    if not resume_text.strip():
        print("Error: No resume text provided. Exiting.")
        return
    
    # Ask if user wants to tailor for a specific role
    role_input = input("\nWould you like to tailor feedback for a specific job role? (Leave blank if not): ")
    role = role_input if role_input.strip() else None
    
    print("\nGenerating feedback...")
    feedback = generate_resume_feedback(resume_text, role)
    
    if feedback:
        print("\n===== Resume Feedback =====")
        
        print("\n✅ STRENGTHS:")
        for i, strength in enumerate(feedback.get("strengths", []), 1):
            print(f"  {i}. {strength}")
        
        print("\n🔍 AREAS FOR IMPROVEMENT:")
        for i, area in enumerate(feedback.get("areas_for_improvement", []), 1):
            print(f"  {i}. {area}")
        
        print("\n📝 SUGGESTED EDITS:")
        for i, suggestion in enumerate(feedback.get("suggested_edits", []), 1):
            print(f"  {i}. {suggestion}")
        
        # Ask if user wants to save the feedback
        save_option = input("\nWould you like to save this feedback to a file? (y/n): ")
        if save_option.lower() == 'y':
            output_path = input("Enter the output file path: ").strip()
            try:
                with open(output_path, 'w', encoding='utf-8') as file:
                    file.write(json.dumps(feedback, indent=2))
                print(f"Feedback saved to {output_path}")
            except Exception as e:
                print(f"Error saving feedback: {str(e)}")
    else:
        print("Failed to generate feedback. Please check your API key and try again.")

def main():
    parser = argparse.ArgumentParser(description='Resume Feedback Generator')
    parser.add_argument('--file', '-f', help='Path to resume file (text or PDF)')
    parser.add_argument('--role', '-r', help='Target job role for tailored feedback')
    parser.add_argument('--output', '-o', help='Output file for the feedback (JSON format)')
    
    args = parser.parse_args()
    
    # If no arguments provided, run in interactive mode
    if not args.file and not sys.argv[1:]:
        interactive_mode()
        return
    
    # Command-line mode
    if args.file:
        if args.file.lower().endswith('.pdf'):
            resume_text = extract_text_from_pdf(args.file)
        else:
            try:
                with open(args.file, 'r', encoding='utf-8') as file:
                    resume_text = file.read()
            except Exception as e:
                print(f"Error reading file: {str(e)}")
                return
        
        if resume_text:
            print(f"Generating feedback for resume from {args.file}...")
            feedback = generate_resume_feedback(resume_text, args.role)
            
            if feedback:
                if args.output:
                    try:
                        with open(args.output, 'w', encoding='utf-8') as file:
                            json.dump(feedback, file, indent=2)
                        print(f"Feedback saved to {args.output}")
                    except Exception as e:
                        print(f"Error saving feedback: {str(e)}")
                else:
                    print(json.dumps(feedback, indent=2))
            else:
                print("Failed to generate feedback.")
    else:
        parser.print_help()

if __name__ == "__main__":
    import sys
    main()
