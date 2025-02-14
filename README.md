# NextGen Resume Analyzer

NextGen Resume Analyzer is an innovative, AI-powered web application built with Streamlit that helps job seekers optimize their resumes. It extracts key information from your resume, evaluates its structure and content, and provides you with a comprehensive analysis including a resume score, an AI-generated summary, skill recommendations, course suggestions, and personalized feedback options.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [Technology Stack](#technology-stack)
- [Developer Information](#developer-information)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Screenshots](#screenshots)
- [Demo App](#demo-app)
- [GitHub Codespaces](#github-codespaces)

---

## Overview

NextGen Resume Analyzer automates the process of resume evaluation. By simply uploading your resume in PDF format, the tool extracts essential details, analyzes your resume's structure and keyword usage, and provides an objective score. Additionally, it generates a tailored AI resume summary along with actionable recommendations to improve your resume’s effectiveness and boost your chances with Applicant Tracking Systems (ATS).

---

## Features

- **Automated Resume Analysis:**  
  Quickly extracts basic information, skills, and a professional summary from your resume, then calculates a resume score based on formatting, ATS optimization, clarity, and overall presentation.

- **AI-Powered Insights:**  
  Generates a concise, AI-based resume summary and provides personalized suggestions—including resume improvement tips and targeted skill/course recommendations.

- **Feedback Submission:**  
  Users can submit feedback on the analysis. Once submitted, feedback is saved with the record and cannot be overridden during the session.

- **Data Export:**  
  Export your complete analysis (including your feedback) as a JSON file for further use or sharing.

- **Dual Dashboards:**  
  - **User Dashboard:** Upload resumes, view detailed analysis, and submit feedback.
  - **Admin Dashboard:** Manage user records, review feedback, download data, clear records, and view visualizations (such as resume score distribution and skills overviews).

---

## How It Works

1. **Upload Your Resume:**  
   In User Mode, upload your resume (in PDF format) using the provided file uploader widget.

2. **Analyze Your Resume:**  
   Click the "Analyze Resume" button. The app extracts text from your PDF and sends it to an AI API for analysis.

3. **View Detailed Results:**  
   Review your resume score, AI-generated summary, current skills, recommended skills, course suggestions, and additional insights like resume tips and matching job roles.

4. **Submit Feedback:**  
   Optionally, provide feedback about your analysis. Once submitted, the feedback is saved with your record and cannot be updated again in the current session.

5. **Export Data:**  
   Download your entire analysis and feedback as a JSON file for your records.

6. **Admin Panel:**  
   Log in to the Admin Dashboard to view all user submissions, manage data, review feedback, and see visual summaries like score distributions and skills statistics.

---

## Installation

### Prerequisites

- Python 3.7 or later
- pip (Python package installer)

### Steps

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/u-faizan/NextGen-Resume-Analyzer.git
   cd NextGen-Resume-Analyzer
   
## Install Dependencies:
bash
pip install -r requirements.txt

## Configure Your API Key:
Create a secrets.toml file (or use your deployment platform’s secret management) with the following:

toml
[API_KEY]
API_KEY = "your_api_key_here"


## Run the Application:
bash
streamlit run streamlit_app.py
Usage
User Mode

## Upload Resume:
Use the "Upload Your Resume" widget to select your PDF resume.

## Analyze Resume:
Click "Analyze Resume" to generate the analysis. The app displays your resume score, AI-generated summary, detailed skills analysis (both current and recommended), course suggestions, and more.

## Submit Feedback:
Enter your feedback (if any) in the provided text area. Once you click "Submit Feedback," the feedback is saved with your record and cannot be changed during the session.

## Export Data:
Download your complete analysis and feedback as a JSON file for future reference.

# Admin Mode
## Log In:
Switch to Admin Mode using the mode selector and log in with your admin credentials.

## Manage Data:
View all user records, download the complete dataset as JSON, clear records, and review visualizations such as resume score distribution and skills overview.

# Technology Stack
Streamlit: For building the interactive web application.

SQLite: For storing user data and feedback.

PDFMiner: For extracting text from PDF resumes.

Pandas & Matplotlib: For data processing and visualization.

Requests: For API communication.

Python: The core programming language used throughout the project.

## Developer Information
Developed by Umar Faizan

linkdin : https://www.linkedin.com/in/u-faizan/

Email: mianumarzareen@gmail.com

GitHub Repository: https://github.com/u-faizan

Feel free to reach out with any questions, feedback, or collaboration opportunities.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
Special thanks to the developers of Streamlit, PDFMiner, and other open-source libraries that made this project possible.
Appreciation to the open-source community for continuous support and valuable resources.

## Screenshots



                              
## Demo App

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://NextGen-Resume-Analyzer.streamlit.app/)

## GitHub Codespaces

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://NextGen-Resume-Analyzer/streamlit/app-starter-kit?quickstart=1)

                                       
