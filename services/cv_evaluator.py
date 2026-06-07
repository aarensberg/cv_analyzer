"""builds the chain and runs the evaluation"""

import logging
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from models.cv_model import CVAnalysis
from prompts.cv_prompts import CHAT_PROMPT

logger = logging.getLogger(__name__)


def build_cv_evaluator():
    base_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

    # Key step: bind the Pydantic schema to the model. The returned runnable
    # delivers a typed CVAnalysis instance instead of free-form text.
    structured_llm = base_llm.with_structured_output(CVAnalysis)

    # Compose the chain with LCEL
    chain = CHAT_PROMPT | structured_llm
    return chain


def evaluate_candidate(cv_text: str, job_description: str) -> Optional[CVAnalysis]:
    """Run the evaluation chain and return a typed CVAnalysis.

    Returns ``None`` if the LLM call fails (network error, missing API key,
    schema-validation error, ...) so a failure surfaces in the UI as a friendly
    message instead of crashing the Streamlit app.
    """
    chain = build_cv_evaluator()
    try:
        return chain.invoke(
            {"cv_text": cv_text, "job_description": job_description}
        )
    except Exception:
        logger.exception("CV evaluation failed")
        return None
