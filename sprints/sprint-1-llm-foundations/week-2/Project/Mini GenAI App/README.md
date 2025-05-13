# Resume Feedback Application

A complete resume feedback application with FastAPI backend and Streamlit frontend.

## Project Structure

```
Mini GenAI App/
├── backend/        # FastAPI backend
│   ├── main.py     # API endpoints
│   ├── .env        # Environment variables
│   └── requirements.txt
│
└── frontend/       # Streamlit frontend
    ├── app.py      # Streamlit application
    ├── .env        # Environment variables
    └── requirements.txt
```

## Features

### Basic Analysis
- Resume text input or file upload (text & PDF)
- Role-specific feedback tailoring option 
- API endpoint for resume feedback generation
- Beautiful Streamlit UI displaying feedback in organized sections
- PDF extraction functionality

### Advanced Analysis
- Detailed resume feedback with numerical scoring
- Experience level and industry-specific targeting
- Keyword analysis for ATS optimization
- Categorized strengths with examples from your resume
- Detailed improvement suggestions with potential impact analysis
- Specific edit recommendations with before/after text
- Export options (JSON and formatted HTML report)

## Setup and Installation

### Backend (FastAPI)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. Start the API server:
   ```bash
   uvicorn main:app --reload
   ```
   The API will be available at http://localhost:8000

5. Alternative API Server
   ```bashs
   py -m uvicorn main:app --reloaad
   ```

### Frontend (Streamlit)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with the API URL:
   ```
   API_URL=http://localhost:8000
   ```

4. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```
   The UI will be available at http://localhost:8501
5. Alternative method to start streamlit app:
   ```bash
   py -m streamlit run app.py
   ```

## API Endpoints

- **POST /resume-feedback**: Process a resume and return concise structured feedback
  - Request body:
    ```json
    {
      "resume_text": "Your resume text here...",
      "role": "Optional job role"
    }
    ```
  - Response:
    ```json
    {
      "strengths": ["strength1", "strength2", "..."],
      "areas_for_improvement": ["area1", "area2", "..."],
      "suggested_edits": ["edit1", "edit2", "..."]
    }
    ```

- **POST /resume-feedback/detailed**: Generate detailed and structured resume feedback
  - Request body:
    ```json
    {
      "resume_text": "Your resume text here...",
      "role": "Optional job role",
      "experience_level": "Senior",
      "industry": "Technology",
      "include_keywords": ["Python", "Machine Learning", "Leadership"]
    }
    ```
  - Response:
    ```json
    {
      "overall_score": 7,
      "strengths": [
        {
          "category": "Technical Skills",
          "description": "Strong technical background",
          "examples_from_resume": ["Proficient in Python", "Led ML projects"]
        }
      ],
      "improvements": [
        {
          "category": "Summary",
          "description": "Too generic",
          "potential_impact": "More specific summary would stand out"
        }
      ],
      "edit_suggestions": [
        {
          "section": "Experience",
          "original_text": "Responsible for...",
          "suggested_text": "Led development of...",
          "reason": "Uses stronger action verb"
        }
      ],
      "keyword_analysis": {
        "present": ["Python", "Leadership"],
        "missing": ["Machine Learning"],
        "suggestions": ["Add ML to skills section"]
      }
    }
    ```

- **GET /health**: Health check endpoint
  - Response:
    ```json
    {
      "status": "healthy"
    }
    ```

- **GET /**: API information endpoint
  - Returns basic information about the API

- **GET /api-schema**: OpenAPI schema endpoint
  - Returns the complete API schema

## Usage

1. Start both the backend and frontend servers in separate terminals
2. Open http://localhost:8501 in your browser
3. Either paste resume text or upload a resume file
4. Optionally select a specific job role for tailored feedback
5. Click "Analyze Resume" to receive AI-generated feedback
