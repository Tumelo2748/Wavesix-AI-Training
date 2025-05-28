import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Set page config
st.set_page_config(
    page_title="Resume Feedback Generator",
    page_icon="📝",
    layout="wide"
)

# Page title
st.title("📝 Resume Feedback Generator")
st.markdown("""
Get professional feedback on your resume using AI. 
Simply paste your resume text below and click 'Analyze Resume'.
""")

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    This application uses AI to analyze your resume and provide feedback.
    
    ### Basic Analysis
    - Resume strengths
    - Areas for improvement
    - Specific edit suggestions
    
    ### Detailed Analysis ✨
    - Overall numerical score
    - Categorized strengths with examples
    - Improvement areas with impact analysis
    - Specific edits with rationale
    - Keyword analysis and suggestions
    
    **Note:** This tool is for educational purposes and should supplement, not replace, professional career advice.
    """)

# Main content
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Your Resume")
    
    tab1, tab2 = st.tabs(["📄 Resume Input", "⚙️ Analysis Options"])
    
    with tab1:
        # File upload option
        uploaded_file = st.file_uploader("Upload a resume (text or PDF)", type=["txt", "pdf"])
        
        # Text input option
        resume_text = st.text_area(
            "Or paste your resume text here:",
            height=300,
            placeholder="Paste your resume content here..."
        )
    
    # If a file was uploaded, read its content
    if uploaded_file is not None:
        try:
            # Check if it's a PDF
            if uploaded_file.name.endswith('.pdf'):
                try:
                    import io
                    import pdfplumber
                    
                    with pdfplumber.open(io.BytesIO(uploaded_file.getvalue())) as pdf:
                        pages_text = [page.extract_text() for page in pdf.pages if page.extract_text()]
                        resume_text = "\n".join(pages_text)
                    
                    st.success("PDF successfully processed!")
                except Exception as e:
                    st.error(f"Error processing PDF: {str(e)}")
                    st.info("Please install pdfplumber: `pip install pdfplumber`")
            else:  # Assume it's a text file
                resume_text = uploaded_file.getvalue().decode("utf-8")
        except Exception as e:            st.error(f"Error reading file: {str(e)}")
    
    with tab2:
        # Basic options
        role_options = ["", "Software Engineer", "Data Scientist", "Product Manager", "Marketing Specialist", "Designer", "Sales Representative", "Other"]
        selected_role = st.selectbox("Tailor feedback for specific role (optional):", role_options)
        
        # If "Other" is selected, allow custom input
        if selected_role == "Other":
            custom_role = st.text_input("Enter the specific role:")
            if custom_role:
                selected_role = custom_role
        
        # Advanced analysis options
        st.markdown("### Advanced Options")
        detailed_analysis = st.toggle("Enable Detailed Analysis", value=False, 
                                     help="Provides more comprehensive feedback with categorized strengths, detailed improvement suggestions, and specific edit recommendations")
        
        # Only show these options if detailed analysis is enabled
        if detailed_analysis:
            experience_level = st.selectbox(
                "Experience Level",
                ["", "Entry-Level", "Mid-Level", "Senior", "Executive"],
                help="Target experience level for the resume"
            )
            
            industry = st.selectbox(
                "Target Industry",
                ["", "Technology", "Healthcare", "Finance", "Education", "Marketing", "Sales", "Manufacturing", "Other"],
                help="Industry to optimize the resume for"
            )
            
            if industry == "Other":
                industry = st.text_input("Enter specific industry:")
            
            st.write("Keywords to check for in the resume:")
            keywords_input = st.text_area(
                "Enter keywords separated by commas (optional)",
                placeholder="e.g., Python, leadership, project management",
                help="The analysis will check for these keywords and suggest how to incorporate missing ones"
            )
            
            # Convert keywords string to list
            keywords = [kw.strip() for kw in keywords_input.split(",")] if keywords_input else []
            
    # Process button
    analyze_button = st.button("Analyze Resume", type="primary")

# Results column
with col2:
    st.subheader("Feedback Results")
    
    if analyze_button:
        if not resume_text.strip():
            st.error("Please provide resume text first.")
        else:            # Show loading spinner
            with st.spinner("Analyzing your resume..."):
                try:
                    # Determine which API endpoint to call
                    if not detailed_analysis:
                        # Call the basic API
                        response = requests.post(
                            f"{API_URL}/resume-feedback",
                            json={
                                "resume_text": resume_text,
                                "role": selected_role if selected_role else None
                            },
                            timeout=30
                        )
                    else:
                        # Call the detailed API
                        response = requests.post(
                            f"{API_URL}/resume-feedback/detailed",
                            json={
                                "resume_text": resume_text,
                                "role": selected_role if selected_role else None,
                                "experience_level": experience_level if experience_level else None,
                                "industry": industry if industry else None,
                                "include_keywords": keywords if keywords else None
                            },
                            timeout=45  # Longer timeout for detailed analysis
                        )
                    
                    # Check if request was successful
                    if response.status_code == 200:
                        feedback = response.json()
                        
                        if not detailed_analysis:
                            # Display basic feedback in expandable sections
                            with st.expander("Strengths", expanded=True):
                                if "strengths" in feedback and feedback["strengths"]:
                                    for strength in feedback["strengths"]:
                                        st.markdown(f"✅ {strength}")
                                else:
                                    st.info("No strengths identified.")
                            
                            with st.expander("Areas for Improvement", expanded=True):
                                if "areas_for_improvement" in feedback and feedback["areas_for_improvement"]:
                                    for area in feedback["areas_for_improvement"]:
                                        st.markdown(f"🔹 {area}")
                                else:
                                    st.info("No areas for improvement identified.")
                            
                            with st.expander("Suggested Edits", expanded=True):
                                if "suggested_edits" in feedback and feedback["suggested_edits"]:
                                    for suggestion in feedback["suggested_edits"]:
                                        st.markdown(f"📝 {suggestion}")
                                else:
                                    st.info("No specific edit suggestions provided.")
                        else:
                            # Display detailed feedback
                            if "overall_score" in feedback:
                                score = feedback["overall_score"]
                                st.markdown(f"### Overall Score: {score}/10")
                                
                                # Create a colored progress bar based on score
                                color = "red" if score < 4 else "orange" if score < 7 else "green"
                                st.progress(score/10, text=f"Resume Rating: {score}/10")
                            
                            # Display strengths with categories
                            with st.expander("Strengths", expanded=True):
                                if "strengths" in feedback and feedback["strengths"]:
                                    for strength in feedback["strengths"]:
                                        st.markdown(f"### {strength['category']}")
                                        st.markdown(f"**{strength['description']}**")
                                        st.markdown("**Examples from your resume:**")
                                        for example in strength['examples_from_resume']:
                                            st.markdown(f"- *\"{example}\"*")
                                        st.markdown("---")
                                else:
                                    st.info("No strengths identified.")
                            
                            # Display improvement areas with potential impact
                            with st.expander("Areas for Improvement", expanded=True):
                                if "improvements" in feedback and feedback["improvements"]:
                                    for improvement in feedback["improvements"]:
                                        st.markdown(f"### {improvement['category']}")
                                        st.markdown(f"**Issue:** {improvement['description']}")
                                        st.markdown(f"**Potential Impact:** {improvement['potential_impact']}")
                                        st.markdown("---")
                                else:
                                    st.info("No areas for improvement identified.")
                            
                            # Display edit suggestions with reasons
                            with st.expander("Suggested Edits", expanded=True):
                                if "edit_suggestions" in feedback and feedback["edit_suggestions"]:
                                    for suggestion in feedback["edit_suggestions"]:
                                        st.markdown(f"### {suggestion['section']}")
                                        if suggestion.get('original_text'):
                                            st.markdown("**Original:**")
                                            st.markdown(f"<div style='background-color:#f0f0f0;padding:10px;border-radius:5px;text-color: #f0f0f0'>{suggestion['original_text']}</div>", unsafe_allow_html=True)
                                        st.markdown("**Suggested:**")
                                        st.markdown(f"<div style='background-color:#e7f7e7;padding:10px;border-radius:5px; text-color: #f0f0f0'>{suggestion['suggested_text']}</div>", unsafe_allow_html=True)
                                        st.markdown(f"**Why:** {suggestion['reason']}")
                                        st.markdown("---")
                                else:
                                    st.info("No specific edit suggestions provided.")
                            
                            # Display keyword analysis if available
                            if "keyword_analysis" in feedback and feedback["keyword_analysis"]:
                                with st.expander("Keyword Analysis", expanded=True):
                                    keyword_data = feedback["keyword_analysis"]
                                    
                                    # Present keywords
                                    if "present" in keyword_data and keyword_data["present"]:
                                        st.markdown("### Keywords Present")
                                        for keyword in keyword_data["present"]:
                                            st.markdown(f"<span style='background-color: #d4edda; padding: 3px 8px; border-radius: 10px; margin-right: 5px;'>{keyword}</span>", unsafe_allow_html=True)
                                    
                                    # Missing keywords
                                    if "missing" in keyword_data and keyword_data["missing"]:
                                        st.markdown("### ❌ Keywords Missing")
                                        for keyword in keyword_data["missing"]:
                                            st.markdown(f"<span style='background-color: #f8d7da; padding: 3px 8px; border-radius: 10px; margin-right: 5px;'>{keyword}</span>", unsafe_allow_html=True)
                                    
                                    # Suggestions for keywords
                                    if "suggestions" in keyword_data and keyword_data["suggestions"]:
                                        st.markdown("### 💡 Keyword Suggestions")
                                        for suggestion in keyword_data["suggestions"]:
                                            st.markdown(f"- {suggestion}")
                            
                        # Add options to save or download the feedback
                        st.markdown("---")
                        st.markdown("### 💾 Save Your Feedback")
                        
                        col_json, col_html = st.columns(2)
                        
                        # Function to convert feedback to a nice HTML report
                        def generate_html_report(feedback_data, detailed=False):
                            import datetime
                            
                            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            role_text = f"for {selected_role}" if selected_role else ""
                            
                            html = f"""
                            <!DOCTYPE html>
                            <html>
                            <head>
                                <title>Resume Feedback Report</title>
                                <style>
                                    body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
                                    h1, h2, h3 {{ color: #2c3e50; }}
                                    .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                                    .section {{ margin-bottom: 30px; }}
                                    .strength {{ background-color: #d4edda; padding: 10px; margin-bottom: 10px; border-radius: 5px; }}
                                    .improvement {{ background-color: #f8d7da; padding: 10px; margin-bottom: 10px; border-radius: 5px; }}
                                    .edit {{ background-color: #e2f0fb; padding: 10px; margin-bottom: 10px; border-radius: 5px; }}
                                    .keyword-present {{ display: inline-block; background-color: #d4edda; padding: 3px 8px; border-radius: 10px; margin-right: 5px; }}
                                    .keyword-missing {{ display: inline-block; background-color: #f8d7da; padding: 3px 8px; border-radius: 10px; margin-right: 5px; }}
                                    .original {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 10px; }}
                                    .suggested {{ background-color: #e7f7e7; padding: 10px; border-radius: 5px; margin-bottom: 10px; }}
                                    .footer {{ text-align: center; margin-top: 50px; font-size: 0.8em; color: #6c757d; }}
                                </style>
                            </head>
                            <body>
                                <div class="header">
                                    <h1>Resume Feedback Report {role_text}</h1>
                                    <p>Generated on {now}</p>
                            """
                            
                            if detailed and "overall_score" in feedback_data:
                                html += f"""
                                    <h2>Overall Score: {feedback_data['overall_score']}/10</h2>
                                    <div style="background-color: #f0f0f0; border-radius: 5px; height: 20px; width: 100%;">
                                        <div style="background-color: {'red' if feedback_data['overall_score'] < 4 else 'orange' if feedback_data['overall_score'] < 7 else 'green'}; width: {feedback_data['overall_score']*10}%; height: 100%; border-radius: 5px;"></div>
                                    </div>
                                """
                            
                            html += """
                                </div>
                            """
                            
                            # Strengths section
                            html += """
                                <div class="section">
                                    <h2>💪 Strengths</h2>
                            """
                            
                            if not detailed:
                                for strength in feedback_data.get("strengths", []):
                                    html += f"""
                                        <div class="strength">
                                            <p>✓ {strength}</p>
                                        </div>
                                    """
                            else:
                                for strength in feedback_data.get("strengths", []):
                                    html += f"""
                                        <div class="strength">
                                            <h3>{strength['category']}</h3>
                                            <p><strong>{strength['description']}</strong></p>
                                            <p><strong>Examples from your resume:</strong></p>
                                            <ul>
                                    """
                                    for example in strength['examples_from_resume']:
                                        html += f"""
                                            <li><em>"{example}"</em></li>
                                        """
                                    html += """
                                            </ul>
                                        </div>
                                    """
                            
                            html += """
                                </div>
                            """
                            
                            # Areas for improvement
                            html += """
                                <div class="section">
                                    <h2>🔍 Areas for Improvement</h2>
                            """
                            
                            if not detailed:
                                for area in feedback_data.get("areas_for_improvement", []):
                                    html += f"""
                                        <div class="improvement">
                                            <p>🔹 {area}</p>
                                        </div>
                                    """
                            else:
                                for improvement in feedback_data.get("improvements", []):
                                    html += f"""
                                        <div class="improvement">
                                            <h3>{improvement['category']}</h3>
                                            <p><strong>Issue:</strong> {improvement['description']}</p>
                                            <p><strong>Potential Impact:</strong> {improvement['potential_impact']}</p>
                                        </div>
                                    """
                            
                            html += """
                                </div>
                            """
                            
                            # Suggested edits
                            html += """
                                <div class="section">
                                    <h2>✏️ Suggested Edits</h2>
                            """
                            
                            if not detailed:
                                for edit in feedback_data.get("suggested_edits", []):
                                    html += f"""
                                        <div class="edit">
                                            <p>📝 {edit}</p>
                                        </div>
                                    """
                            else:
                                for suggestion in feedback_data.get("edit_suggestions", []):
                                    html += f"""
                                        <div class="edit">
                                            <h3>{suggestion['section']}</h3>
                                    """
                                    if suggestion.get('original_text'):
                                        html += f"""
                                            <p><strong>Original:</strong></p>
                                            <div class="original">{suggestion['original_text']}</div>
                                        """
                                    html += f"""
                                            <p><strong>Suggested:</strong></p>
                                            <div class="suggested">{suggestion['suggested_text']}</div>
                                            <p><strong>Why:</strong> {suggestion['reason']}</p>
                                        </div>
                                    """
                            
                            html += """
                                </div>
                            """
                            
                            # Keyword analysis for detailed feedback
                            if detailed and "keyword_analysis" in feedback_data:
                                keyword_data = feedback_data["keyword_analysis"]
                                html += """
                                    <div class="section">
                                        <h2>🔑 Keyword Analysis</h2>
                                """
                                
                                if "present" in keyword_data and keyword_data["present"]:
                                    html += """
                                        <h3>✓ Keywords Present</h3>
                                        <p>
                                    """
                                    for keyword in keyword_data["present"]:
                                        html += f"""
                                            <span class="keyword-present">{keyword}</span>
                                        """
                                    html += """
                                        </p>
                                    """
                                
                                if "missing" in keyword_data and keyword_data["missing"]:
                                    html += """
                                        <h3>❌ Keywords Missing</h3>
                                        <p>
                                    """
                                    for keyword in keyword_data["missing"]:
                                        html += f"""
                                            <span class="keyword-missing">{keyword}</span>
                                        """
                                    html += """
                                        </p>
                                    """
                                
                                if "suggestions" in keyword_data and keyword_data["suggestions"]:
                                    html += """
                                        <h3>💡 Keyword Suggestions</h3>
                                        <ul>
                                    """
                                    for suggestion in keyword_data["suggestions"]:
                                        html += f"""
                                            <li>{suggestion}</li>
                                        """
                                    html += """
                                        </ul>
                                    """
                                
                                html += """
                                    </div>
                                """
                            
                            html += """
                                <div class="footer">
                                    <p>Generated by Resume Feedback Generator</p>
                                </div>
                            </body>
                            </html>
                            """
                            
                            return html
                        
                        # Generate JSON and HTML
                        json_data = json.dumps(feedback, indent=2)
                        html_report = generate_html_report(feedback, detailed_analysis)
                        
                        # Download buttons
                        with col_json:
                            st.download_button(
                                label="Download JSON",
                                data=json_data,
                                file_name=f"resume_feedback_{selected_role or 'general'}.json",
                                mime="application/json",
                            )
                        
                        with col_html:
                            st.download_button(
                                label="Download HTML Report",
                                data=html_report,
                                file_name=f"resume_feedback_{selected_role or 'general'}.html",
                                mime="text/html",
                            )
                                
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                
                except requests.exceptions.ConnectionError:
                    st.error("Connection error. Make sure the API server is running.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

