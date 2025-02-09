import streamlit as st
from pdfminer.high_level import extract_text

# Function to extract text from PDF using pdfminer

def extract_text_from_pdf(uploaded_file):
    if uploaded_file is not None:
        with open("temp_resume.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())  # Save uploaded file locally
        
        # Extract text from the saved PDF
        extracted_text = extract_text("temp_resume.pdf")
        return extracted_text
    else:
        return "No file uploaded."

# Streamlit App Interface
st.title("Smart Resume Analyzer")

uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

if uploaded_file:
    st.success("File uploaded successfully!")
    
    # Extract and display text
    resume_text = extract_text_from_pdf(uploaded_file)
    st.subheader("Extracted Resume Text")
    st.text(resume_text[:1500] + "...")
