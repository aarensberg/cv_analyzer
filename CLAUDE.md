# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status: scaffold only

This is a course assignment for Albert School's "Introduction to Generative AI and LLMs". **Every Python file currently contains nothing but a one-line docstring describing its role — none of the logic exists yet.** The full specification, step-by-step instructions, required `CVAnalysis` fields, and prompt requirements live in `guidelines.pdf`. Read it before implementing anything; it is the source of truth, not the code.

The goal: a modular Streamlit app that reads a candidate's CV (PDF) plus a job description and returns a **typed Pydantic `CVAnalysis` object** (not free-form text) for the UI to render. The pedagogical centerpiece is `llm.with_structured_output(CVAnalysis)`.

## Commands

The virtualenv (`.venv/`) exists but is empty — there is no `requirements.txt`. Install dependencies before running:

```bash
.venv/bin/pip install streamlit pydantic PyPDF2 langchain langchain-core langchain-google-genai
```

Run the app (must be from the project root — see Imports below):

```bash
.venv/bin/streamlit run app.py
```

The LLM is Google Gemini (`gemini-2.5-flash`) via `langchain-google-genai`, which requires a Gemini API key in the environment (e.g. `GOOGLE_API_KEY`) before evaluation will work.

## Architecture

Single-responsibility modules with a one-directional data flow:

```
app.py            → calls ui.streamlit_ui.main()
ui/streamlit_ui.py → collects PDF + job description, orchestrates, renders the CVAnalysis
services/pdf_processor.py  → extract_pdf_text(uploaded_file) -> str   (PyPDF2)
services/cv_evaluator.py   → build_cv_evaluator() builds an LCEL chain (CHAT_PROMPT | structured_llm);
                             evaluate_candidate(cv_text, job_description) -> CVAnalysis
prompts/cv_prompts.py      → CHAT_PROMPT: system (recruiter persona) + human ({job_description}, {cv_text})
models/cv_model.py         → CVAnalysis (Pydantic BaseModel) — the schema the LLM must match
```

Flow: UI uploads PDF → `extract_pdf_text` → `evaluate_candidate(cv_text, job_description)` → chain `CHAT_PROMPT | base_llm.with_structured_output(CVAnalysis)` → typed `CVAnalysis` back to UI for rendering.

Key contracts that span multiple files:

- **The Pydantic schema is the LLM's instruction set.** Each `Field(description=...)` on `CVAnalysis` is sent to the model as part of the structured-output contract — descriptions are functional, not documentation. Required fields per the spec: `candidate_name`, `years_of_experience` (int), `key_skills` (5–7), `education`, `relevant_experience`, `strengths` (3–5), `areas_for_improvement` (2–4), `fit_percentage` (int, constrained `ge=0, le=100`).
- **Prompt takes two template variables at once**: `{job_description}` and `{cv_text}`. The chain is invoked with both.
- **Imports are absolute from the project root** (`from models.cv_model import ...`, `from services.cv_evaluator import ...`). There are no `__init__.py` files and no package install, so the app only resolves these when launched from the repo root.

## Implementation notes from the spec

- `evaluate_candidate` must wrap the chain `.invoke(...)` in try/except so an LLM failure does not crash the Streamlit UI.
- `extract_pdf_text` should skip empty pages and return a clear error string for image-only/scanned PDFs (no selectable text) so the UI can detect the failure.
- The UI is a two-column layout (inputs left, results right) and should show progress (e.g. a spinner) while the LLM generates.
