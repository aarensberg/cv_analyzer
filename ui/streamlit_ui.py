"""all Streamlit components"""

import streamlit as st
from models.cv_model import CVAnalysis
from services.pdf_processor import extract_pdf_text, PDF_ERROR_PREFIX
from services.cv_evaluator import evaluate_candidate


def main():
    st.set_page_config(page_title="CV Evaluation System", layout="wide")
    st.title("CV Evaluation System")
    st.caption(
        "Upload a candidate's CV and a job description — an AI recruiter returns "
        "a structured fit analysis."
    )

    # Two columns: inputs on the left, results on the right
    col_input, col_result = st.columns([1, 1], gap="large")

    with col_input:
        st.subheader("Inputs")

        # 1. File uploader for the PDF CV
        uploaded_file = st.file_uploader("Candidate CV (PDF)", type=["pdf"])

        # 2. Text area for the job description
        job_description = st.text_area(
            "Job description",
            height=320,
            placeholder="Paste the full job description here…",
        )

        # 3. "Analyze candidate" button
        analyze = st.button("Analyze candidate", type="primary")

    with col_result:
        st.subheader("Analysis")

        # If the button was clicked AND both inputs are present:
        if analyze:
            if uploaded_file is None:
                st.warning("Please upload a CV in PDF format first.")
            elif not job_description.strip():
                st.warning("Please paste the job description first.")
            else:
                # - extract the PDF text
                with st.spinner("Extracting text from the PDF…"):
                    cv_text = extract_pdf_text(uploaded_file)

                if cv_text.startswith(PDF_ERROR_PREFIX):
                    st.error(cv_text)
                else:
                    # - call evaluate_candidate(...)
                    with st.spinner("The AI recruiter is analyzing the candidate…"):
                        result = evaluate_candidate(cv_text, job_description)

                    # - render the resulting CVAnalysis object
                    if result is None:
                        st.error(
                            "The analysis failed. Please check that your "
                            "GOOGLE_API_KEY is set in .env and try again."
                        )
                    else:
                        render_results(result)
        else:
            st.info(
                "Upload a CV, paste a job description, then click "
                "**Analyze candidate**."
            )


def _fit_verdict(fit: int) -> tuple[str, str]:
    """Map a fit percentage to a qualitative label and a hiring recommendation."""
    if fit >= 80:
        return "Excellent match", "✅ Strong hire — move the candidate to interview."
    if fit >= 60:
        return "Good match", "👍 Promising — worth an interview."
    if fit >= 40:
        return "Average match", "🤔 Borderline — consider only if the pipeline is thin."
    return "Low match", "❌ Not recommended for this role."


def render_results(result: CVAnalysis):
    label, recommendation = _fit_verdict(result.fit_percentage)

    # - A big metric showing result.fit_percentage with a qualitative label
    st.metric("Fit for the role", f"{result.fit_percentage}%")
    st.progress(result.fit_percentage / 100, text=f"**{label}**")

    st.divider()

    # - The candidate's name, years of experience, and education
    st.markdown(f"### {result.candidate_name}")
    col_a, col_b = st.columns(2)
    col_a.metric("Years of experience", result.years_of_experience)
    col_b.markdown(f"**Education**  \n{result.education}")

    # - The relevant_experience summary
    st.markdown("#### Relevant experience")
    st.write(result.relevant_experience)

    # - The key_skills as badges
    st.markdown("#### Key skills")
    st.markdown(" ".join(f":blue-badge[{skill}]" for skill in result.key_skills))

    # - Two side-by-side columns for strengths and areas_for_improvement
    st.markdown("#### Assessment")
    strengths_col, improvements_col = st.columns(2)
    with strengths_col:
        st.markdown("**Strengths**")
        for strength in result.strengths:
            st.success(strength)
    with improvements_col:
        st.markdown("**Areas for improvement**")
        for area in result.areas_for_improvement:
            st.warning(area)

    # - A final hire / no-hire recommendation derived from fit_percentage
    st.markdown("#### Recommendation")
    st.info(recommendation)
