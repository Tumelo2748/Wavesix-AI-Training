import os
import json
import logging
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import openai
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Create FastAPI app
app = FastAPI(
    title="Resume Feedback API", 
    description="API for analyzing resumes and providing feedback",
    version="1.0.0"
)

# Add custom error handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development (restrict in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request models
class ResumeRequest(BaseModel):
    resume_text: str = Field(..., description="The resume text to analyze")
    role: Optional[str] = Field(None, description="Target job role for tailored feedback")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "resume_text": "Tumelo\nSoftware Engineer\n5+ years experience in Python development...",
                "role": "Data Scientist"
            },
            "examples": [
                {
                    "resume_text": "Lasmen Die\nProduct Manager\n8+ years experience leading product teams...",
                    "role": "Product Manager"
                },
                {
                    "resume_text": "Alex Pops\nData Analyst\n3 years experience in data visualization...",
                    "role": None
                }
            ]
        }
    }

class ResumeRequestDetailed(ResumeRequest):
    experience_level: Optional[str] = Field(None, 
        description="Experience level to target (e.g. 'Entry', 'Mid', 'Senior')")
    industry: Optional[str] = Field(None, 
        description="Industry to tailor feedback for (e.g. 'Tech', 'Finance', 'Healthcare')")
    include_keywords: Optional[List[str]] = Field(None, 
        description="List of keywords to check for in the resume")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "resume_text": "Tumelo\nSoftware Engineer\n5+ years experience in Python development...",
                "role": "Data Scientist",
                "experience_level": "Senior",
                "industry": "Tech",
                "include_keywords": ["Python", "Machine Learning", "Data Analysis"]
            }
        }
    }

# Define response models for specific sections
class StrengthFeedback(BaseModel):
    category: str = Field(..., description="Category of strength (e.g. 'Technical', 'Communication')")
    description: str = Field(..., description="Detailed description of the strength")
    examples_from_resume: List[str] = Field(..., description="Examples from the resume that demonstrate this strength")

class ImprovementFeedback(BaseModel):
    category: str = Field(..., description="Category needing improvement (e.g. 'Format', 'Content')")  
    description: str = Field(..., description="Description of the area for improvement")
    potential_impact: str = Field(..., description="How improving this could impact the resume's effectiveness")

class EditSuggestion(BaseModel):
    section: str = Field(..., description="Section of the resume for this edit (e.g. 'Summary', 'Experience')")
    original_text: Optional[str] = Field(None, description="Original text to be replaced (if applicable)")
    suggested_text: str = Field(..., description="Suggested text or edit")
    reason: str = Field(..., description="Reason for making this edit")

# Define response models
class ResumeFeedback(BaseModel):
    strengths: List[str] = Field(..., description="List of resume strengths identified")
    areas_for_improvement: List[str] = Field(..., description="List of areas that could be improved")
    suggested_edits: List[str] = Field(..., description="List of specific suggested edits")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "strengths": [
                    "Strong technical skills with Python and data analysis",
                    "Clear quantification of achievements",
                    "Relevant experience in the target industry"
                ],
                "areas_for_improvement": [
                    "Summary section is too generic",
                    "Skills section could be more organized",
                    "Education section lacks relevant coursework"
                ],
                "suggested_edits": [
                    "Replace 'Responsible for' with action verbs like 'Led' or 'Implemented'",
                    "Add specific Python libraries and frameworks you've worked with",
                    "Quantify the impact of your projects with metrics"
                ]
            }
        }
    }

class DetailedResumeFeedback(BaseModel):
    overall_score: int = Field(..., ge=1, le=10, description="Overall score of the resume on a scale of 1-10")
    strengths: List[StrengthFeedback] = Field(..., description="Detailed analysis of resume strengths")
    improvements: List[ImprovementFeedback] = Field(..., description="Detailed analysis of improvement areas")
    edit_suggestions: List[EditSuggestion] = Field(..., description="Detailed suggestions for edits")
    keyword_analysis: Optional[dict] = Field(None, description="Analysis of requested keywords")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "overall_score": 7,
                "strengths": [
                    {
                        "category": "Technical Skills",
                        "description": "Strong, relevant technical skillset for the target role",
                        "examples_from_resume": ["Proficient in Python, SQL, and data visualization"]
                    },
                    {
                        "category": "Achievement Focus",
                        "description": "Good use of metrics to quantify achievements",
                        "examples_from_resume": ["Increased user engagement by 40%", "Reduced system latency by 30%"]
                    }
                ],
                "improvements": [
                    {
                        "category": "Summary",
                        "description": "Professional summary lacks specificity and unique value proposition",
                        "potential_impact": "A more targeted summary could immediately grab the recruiter's attention"
                    },
                    {
                        "category": "Skills Organization",
                        "description": "Skills are listed without clear categorization",
                        "potential_impact": "Organized skills make it easier for ATS systems to identify relevant qualifications"
                    }
                ],
                "edit_suggestions": [
                    {
                        "section": "Professional Summary",
                        "original_text": "Dynamic team player with 5+ years of experience in software development.",
                        "suggested_text": "Results-driven Software Engineer with 5+ years of experience building scalable web applications that improved user engagement by 40%.",
                        "reason": "Adds specificity and quantifiable achievements to create immediate impact"
                    },
                    {
                        "section": "Experience - Senior Software Engineer",
                        "original_text": "Responsible for development of company's flagship product",
                        "suggested_text": "Led development of company's flagship product, resulting in 40% increase in user engagement",
                        "reason": "Replaces passive voice with action verb and includes metrics"
                    }
                ],
                "keyword_analysis": {
                    "present": ["Python", "Data Analysis"],
                    "missing": ["Machine Learning"],
                    "suggestions": ["Consider adding 'Machine Learning' to your skills section if you have experience with it"]
                }
            }
        }
    }

@app.post("/resume-feedback", response_model=ResumeFeedback, tags=["Resume Analysis"])
async def generate_feedback(request: ResumeRequest):
    """
    Generate concise feedback for a resume using OpenAI's GPT model.
    
    This endpoint provides a simple analysis with:
    - Resume strengths (3-5 points)
    - Areas for improvement (3-5 points)
    - Suggested edits for wording and formatting (3-5 suggestions)
    
    For a more detailed analysis, use the /resume-feedback/detailed endpoint.
    """
    if not request.resume_text:
        raise HTTPException(status_code=400, detail="Resume text is required")
    
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    # Build the prompt
    role_context = f" for a {request.role} position" if request.role else ""
    
    prompt = f"""You are a professional career coach specializing in resume optimization. Analyze the following resume{role_context} and provide detailed feedback in three categories:
1. Strengths: Highlight 3-5 key strengths of the resume.
2. Areas for Improvement: Identify 3-5 areas where the resume could be improved.
3. Suggested Edits: Provide 3-5 actionable suggestions for improving wording, formatting, or content.

Here is the resume to analyze:
---
{request.resume_text}

Please return your feedback in a well-structured JSON format as follows:
{{
    "strengths": ["Highlight 1", "Highlight 2", ...],
    "areas_for_improvement": ["Improvement 1", "Improvement 2", ...],
    "suggested_edits": ["Edit 1", "Edit 2", ...]
}}
Ensure your feedback is clear, concise, and actionable.
"""
    
    try:
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
        
        # Parse the JSON response
        feedback_str = response.choices[0].message.content
        import json
        feedback_dict = json.loads(feedback_str)
        
        # Validate the response structure
        required_keys = ["strengths", "areas_for_improvement", "suggested_edits"]
        if not all(key in feedback_dict for key in required_keys):
            raise ValueError("Incomplete response structure")
            
        return feedback_dict
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating feedback: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}

@app.post("/resume-feedback/detailed", response_model=DetailedResumeFeedback, tags=["Resume Analysis"])
async def generate_detailed_feedback(request: ResumeRequestDetailed):
    """
    Generate detailed and structured feedback for a resume using OpenAI's GPT model.
    
    This endpoint provides more comprehensive analysis including:
    - Numerical score
    - Categorized strengths with examples
    - Detailed improvement suggestions with potential impact
    - Specific edit recommendations with rationale
    - Keyword analysis (if keywords are provided)
    
    Perfect for in-depth resume review and ATS optimization.
    """
    if not request.resume_text:
        raise HTTPException(status_code=400, detail="Resume text is required")
    
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    # Build context from additional parameters
    context_parts = []
    if request.role:
        context_parts.append(f"for a {request.role} position")
    if request.experience_level:
        context_parts.append(f"at the {request.experience_level} level")
    if request.industry:
        context_parts.append(f"in the {request.industry} industry")
    
    context = " ".join(context_parts)
    if context:
        context = " " + context
    
    # Add keyword analysis if requested
    keyword_prompt = ""
    if request.include_keywords and len(request.include_keywords) > 0:
        keywords_list = ", ".join(request.include_keywords)
        keyword_prompt = f"""
Also analyze if the following keywords appear in the resume: {keywords_list}. 
For each keyword, indicate if it's present or missing, and suggest how to incorporate missing keywords if relevant to the candidate's background.
Include this analysis in the keyword_analysis section of your response.
"""
    
    prompt = f"""You are a professional career coach and ATS (Applicant Tracking System) expert specializing in resume optimization. 
Provide an in-depth analysis of the following resume{context} with detailed, actionable feedback.

First, rate the resume on a scale of 1-10, with 10 being exceptional.

Then provide detailed feedback in these categories:
1. Strengths: Identify 2-3 key strengths, categorize each strength, provide a detailed explanation, and cite specific examples from the resume.
2. Areas for Improvement: Identify 2-3 improvement areas, categorize each area, explain the issue, and describe the potential impact of improving it.
3. Edit Suggestions: Provide 2-3 specific edit recommendations, identify the section they apply to, quote the original text when applicable, suggest new wording, and explain the reasoning behind each change.
{keyword_prompt}

Here is the resume to analyze:
---
{request.resume_text}

Please return your feedback in the following JSON format:
{{
  "overall_score": <score between 1-10>,
  "strengths": [
    {{
      "category": "<strength category>",
      "description": "<detailed description>",
      "examples_from_resume": ["<example1>", "<example2>", ...]
    }},
    ...
  ],
  "improvements": [
    {{
      "category": "<improvement category>",
      "description": "<detailed description>",
      "potential_impact": "<impact of making this improvement>"
    }},
    ...
  ],
  "edit_suggestions": [
    {{
      "section": "<resume section>",
      "original_text": "<text to replace or null if not applicable>",
      "suggested_text": "<suggested revision>",
      "reason": "<explanation of why this change helps>"
    }},
    ...
  ],
  "keyword_analysis": {{
    "present": ["<keyword1>", ...],
    "missing": ["<keyword2>", ...],
    "suggestions": ["<suggestion1>", ...]
  }}
}}

Ensure your feedback is specific, actionable, and tailored to the resume and context provided.
"""
    
    try:
        # Call the OpenAI API
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert resume analyst specializing in ATS optimization and career coaching."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,  # Lower temperature for more consistent, structured output
            response_format={"type": "json_object"}
        )
        
        # Parse the JSON response
        feedback_str = response.choices[0].message.content
        feedback_dict = json.loads(feedback_str)
        
        # Ensure None instead of null for optional fields
        for suggestion in feedback_dict.get("edit_suggestions", []):
            if "original_text" in suggestion and suggestion["original_text"] is None:
                suggestion["original_text"] = None
        
        return feedback_dict
        
    except Exception as e:
        logger.error(f"Error generating detailed feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating feedback: {str(e)}")

@app.get("/", tags=["System"])
async def api_info():
    """
    Get information about the API.
    """
    return {
        "name": "Resume Feedback API",
        "version": "1.0.0",
        "description": "API for analyzing resumes and providing feedback using AI",
        "endpoints": {
            "resume-feedback": "Generate concise feedback for a resume",
            "resume-feedback/detailed": "Generate detailed and structured feedback for a resume",
            "health": "Health check endpoint"
        },
        "documentation": "/docs"
    }

@app.get("/api-schema", tags=["System"])
async def api_schema():
    """
    Get the OpenAPI schema for this API.
    """
    return app.openapi()
