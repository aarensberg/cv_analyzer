"""all Streamlit components"""

import streamlit as st
from models.cv_model import CVAnalysis
from services.pdf_processor import extract_pdf_text
from services.cv_evaluator import evaluate_candidate


def main():
    st.set_page_config(page_title="CV Evaluation System", layout="wide")
    st.title("CV Evaluation System")

    # Two columns: inputs on the left, results on the right
    col_input, col_result = st.columns([1, 1], gap="large")

    with col_input:
        # 1. File uploader for the PDF CV
        # 2. Text area for the job description
        # 3. "Analyze candidate" button
        ...

    with col_result:
        # If the button was clicked AND both inputs are present:
        # - extract the PDF text
        # - call evaluate_candidate(...)
        # - render the resulting CVAnalysis object
        ...


def render_results(result: CVAnalysis):
    # Suggested layout:
    # - A big metric showing result.fit_percentage with a qualitative label
    # (e.g. >=80 Excellent, >=60 Good, >=40 Average, <40 Low)
    # - The candidate's name, years of experience, and education
    # - The relevant_experience summary
    # - The key_skills as badges or success boxes
    # - Two side-by-side columns for strengths and areas_for_improvement
    # - A final hire / no-hire recommendation derived from fit_percentage
    ...
