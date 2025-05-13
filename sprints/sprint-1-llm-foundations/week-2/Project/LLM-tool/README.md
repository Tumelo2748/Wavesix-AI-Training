# Resume Feedback Tools

This repository contains two implementations of a resume feedback tool that uses OpenAI's GPT models to provide feedback on resumes:

1. **Standalone Python Tool** - A command-line tool for analyzing resumes
2. **Full Web Application** - A complete web app with FastAPI backend and Streamlit frontend



## 1. Standalone Python Tool

### Features

- Analyze resume text and provide structured feedback
- Input via text paste, text file, or PDF file
- Option to tailor feedback for specific job roles
- Command-line arguments for batch processing
- Interactive mode for step-by-step guidance

### Usage

Run the enhanced version of the script:

```bash
python resume_feedback_enhanced.py
```

#### Command-line Arguments

```bash
python resume_feedback_enhanced.py --file path/to/resume.pdf --role "Data Scientist" --output feedback.json
```

## 2. Full Web Application

### Features

- FastAPI backend with documented API endpoints
- Beautiful Streamlit frontend
- Resume input via text paste or file upload (text and PDF)
- Role-specific feedback tailoring
- Clean visualization of feedback results

### Running the Application

#### On Windows

```bash
cd full_app
start_app.bat
```

#### On Linux/Mac

```bash
cd full_app
bash start_app.sh
```

Or start the components separately:

```bash
# Backend
cd full_app/backend
uvicorn main:app --reload

# Frontend
cd full_app/frontend
streamlit run app.py
```

## Example Output

```json
{
    "strengths": [
        "Strong leadership and project management experience",
        "Quantified achievements with clear impact",
        "Diverse technical skills applicable to various roles"
    ],
    "areas_for_improvement": [
        "Too much jargon in the summary section",
        "Lacks technical skills for target role",
        "Employment gaps not explained"
    ],
    "suggested_edits": [
        "Rephrase 'dynamic team player' to 'led a cross-functional team of 8 engineers'",
        "Add Python and SQL to skills section if applicable",
        "Use more action verbs at the beginning of bullet points"
    ]
}
```

## API Documentation

When running the full application, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
