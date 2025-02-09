import streamlit as st
import json
import re

def extract_json(response):
    """Extract and validate JSON from the model response."""
    json_match = re.search(r'\{.*\}', response, re.DOTALL)  # Find the JSON part
    if json_match:
        json_text = json_match.group(0)  # Extract JSON part
        try:
            return json.loads(json_text)  # Convert JSON string to Python dictionary
        except json.JSONDecodeError:
            st.error("Error: The extracted JSON is not valid.")
    else:
        st.error("Error: No valid JSON found in the response.")
    return {}

def display_course_recommendations(courses):
    """Safely display recommended courses."""
    st.header("Recommended Courses")
    if isinstance(courses, list) and courses:
        for course in courses:
            if isinstance(course, dict) and all(key in course for key in ["platform", "course_name", "link"]):
                st.markdown(f"- **{course['platform']}**: [{course['course_name']}]({course['link']})")
            else:
                st.warning("Invalid course format detected. Skipping entry.")
    else:
        st.info("No recommended courses found.")

# Streamlit App UI
st.title("NextGen Resume Analyzer")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    resume_text = "Extracted text from PDF here..."  # Replace with actual text extraction logic
    
    # Placeholder: Send `resume_text` to an AI model and get `response`
    response = """{
        "basic_info": {
            "name": "John Doe",
            "email": "johndoe@example.com",
            "mobile": "1234567890",
            "address": "123 Main St, City"
        },
        "skills": {
            "current_skills": ["Python", "Machine Learning", "Data Science"],
            "recommended_skills": ["Deep Learning", "NLP", "Cloud Computing"]
        },
        "course_recommendations": [
            {"platform": "Coursera", "course_name": "AI for Everyone", "link": "https://www.coursera.org/learn/ai-for-everyone"},
            {"platform": "Udemy", "course_name": "Python for Data Science", "link": "https://www.udemy.com/course/python-for-data-science/"}
        ],
        "resume_score": "80/100"
    }"""  # Simulated response

    structured_data = extract_json(response)
    
    if structured_data:
        # Display basic info
        basic_info = structured_data.get("basic_info", {})
        st.subheader("Basic Information")
        st.write(f"**Name:** {basic_info.get('name', 'N/A')}")
        st.write(f"**Email:** {basic_info.get('email', 'N/A')}")
        st.write(f"**Mobile:** {basic_info.get('mobile', 'N/A')}")
        st.write(f"**Address:** {basic_info.get('address', 'N/A')}")
        
        # Display skills
        skills = structured_data.get("skills", {})
        st.subheader("Skills")
        st.write("**Current Skills:**", ", ".join(skills.get("current_skills", [])))
        st.write("**Recommended Skills:**", ", ".join(skills.get("recommended_skills", [])))
        
        # Display course recommendations
        display_course_recommendations(structured_data.get("course_recommendations", []))
        
        # Display resume score
        st.subheader("Resume Score")
        st.write(f"Your resume score is: {structured_data.get('resume_score', 'N/A')}")
