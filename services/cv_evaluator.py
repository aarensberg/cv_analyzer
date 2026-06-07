"""builds the chain and runs the evaluation"""

from langchain_google_genai import ChatGoogleGenerativeAI
from models.cv_model import CVAnalysis
from prompts.cv_prompts import CHAT_PROMPT


def build_cv_evaluator():
    base_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

    # Key step: bind the Pydantic schema to the model
    structured_llm = base_llm.with_structured_output(CVAnalysis)

    # Compose the chain with LCEL
    chain = CHAT_PROMPT | structured_llm
    return chain


def evaluate_candidate(cv_text: str, job_description: str) -> CVAnalysis:
    chain = build_cv_evaluator()
    # Your turn — invoke the chain with both inputs and return the result.
    # Wrap the call in try/except so a failure doesn't crash the UI.
    ...
