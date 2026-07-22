import streamlit as st
from google import genai
import PyPDF2

# Page Setup
st.set_page_config(page_title="AI Candidate Ranker", layout="wide")
st.title("🕵️‍♂️ Private Candidate Ranker")
st.write("Upload a Job Description and multiple CVs to get instant rankings.")

# Sidebar for API Key (Secure and Private)
api_key = st.sidebar.text_input("Enter your Gemini API Key", type="password")

def extract_text(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    return "".join([page.extract_text() for page in reader.pages])

# File Uploaders
col1, col2 = st.columns(2)
with col1:
    jd_file = st.file_uploader("Upload Job Description (PDF)", type="pdf")
with col2:
    cv_files = st.file_uploader("Upload CVs (PDFs)", type="pdf", accept_multiple_files=True)

# Processing
if jd_file and cv_files and api_key:
    if st.button("Rank Candidates"):
        # Initialize client for AQ keys
        client = genai.Client(api_key=api_key)
        
        jd_text = extract_text(jd_file)
        
        with st.spinner("Analyzing profiles..."):
            cv_data = []
            for cv in cv_files:
                cv_text = extract_text(cv)
                cv_data.append(f"Candidate: {cv.name}\n{cv_text}")
            
            combined_cvs = "\n\n---\n\n".join(cv_data)
            
            prompt = f"""
            Act as an expert recruiter. Compare the Job Description with the provided candidates.
            
            Job Description:
            {jd_text}
            
            Candidates:
            {combined_cvs}
            
            Task:
            1. Rank the candidates from best fit to worst fit.
            2. For each candidate, provide a score (0-100), top 3 strengths, and top 2 weaknesses/gaps.
            3. Present this in a clear, formatted Markdown table followed by brief explanations.
            """
            
            # Using the stable general model ID supported by AQ keys
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
            )
            st.markdown(response.text)
            
elif not api_key:
    st.warning("Please enter your Gemini API Key in the sidebar to start.")
