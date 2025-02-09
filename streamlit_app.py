import streamlit as st
import fitz  # PyMuPDF for PDF text extraction

def extract_text_from_pdf(uploaded_file):
    if uploaded_file is not None:
        # Read file as bytes
        pdf_bytes = uploaded_file.read()
        
        # Open the PDF from bytes
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Extract text
        extracted_text = ""
        for page in pdf_document:
            extracted_text += page.get_text()
        return extracted_text
    else:
        return "No file uploaded."

# Streamlit App Interface
st.title("📄 Smart Resume Analyzer")

uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

if uploaded_file:
    st.success("File uploaded successfully!")
    
    # Extract and display text
    resume_text = extract_text_from_pdf(uploaded_file)
    st.subheader("Extracted Resume Text")
    st.text(resume_text[:500] + "...")
