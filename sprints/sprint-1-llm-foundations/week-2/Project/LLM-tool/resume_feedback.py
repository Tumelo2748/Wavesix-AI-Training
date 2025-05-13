import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_resume_feedback(resume_text, role=None):
    """
    Generate feedback for a resume using OpenAI's GPT model.
    
    Args:
        resume_text (str): The resume text to analyze
        role (str, optional): Target job role to tailor feedback for
    
    Returns:
        dict: Structured feedback including strengths, areas for improvement, and suggestions
    """
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
    try:
        feedback = response.choices[0].message.content
        return feedback
    except Exception as e:
        return {
            "error": f"Failed to parse feedback: {str(e)}",
            "raw_response": response
        }

def main():
    print("Resume Feedback Generator")
    print("------------------------")
    
    # Get resume text from user
    print("Please paste your resume text below (type 'DONE' on a new line when finished):")
    resume_lines = []
    while True:
        line = input()
        if line == "DONE":
            break
        resume_lines.append(line)
    
    resume_text = "\n".join(resume_lines)
    
    # Ask if user wants to tailor for a specific role
    role_input = input("Would you like to tailor feedback for a specific job role? (Leave blank if not): ")
    role = role_input if role_input.strip() else None
    
    print("\nGenerating feedback...")
    feedback = generate_resume_feedback(resume_text, role)
    
    print("\nResume Feedback:")
    print("---------------")
    print(feedback)

if __name__ == "__main__":
    main()
