# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status: starter skeletons, core logic unfinished

This is a course assignment for Albert School's "Introduction to Generative AI and LLMs". The files now hold the **starter skeletons copied verbatim from `guidelines.pdf`**, but the actual logic is still marked with `...` / `# Your turn` TODOs. The full specification, step-by-step instructions, required `CVAnalysis` fields, and prompt requirements live in `guidelines.pdf` — it is the source of truth, not the code. Read it before implementing.

What is wired vs. what still needs to be written:

- `app.py` — done (entry point).
- `services/cv_evaluator.py` — `build_cv_evaluator()` done; **`evaluate_candidate()` body is a TODO** (invoke the chain, wrap in try/except).
- `models/cv_model.py` — only `candidate_name` exists; **the other 7 fields are TODO** (see schema below).
- `prompts/cv_prompts.py` — `SYSTEM_PROMPT` and `ANALYSIS_PROMPT` are placeholder `"""..."""` strings; **both need real text**.
- `services/pdf_processor.py` — `extract_pdf_text()` body is a TODO.
- `ui/streamlit_ui.py` — `main()` input/result blocks and `render_results()` are TODOs.

The goal: a modular Streamlit app that reads a candidate's CV (PDF) plus a job description and returns a **typed Pydantic `CVAnalysis` object** (not free-form text) for the UI to render. The pedagogical centerpiece is `llm.with_structured_output(CVAnalysis)`.

## Commands

Dependencies are pinned in `requirements.txt`. Install into the existing `.venv/`:

```bash
.venv/bin/pip install -r requirements.txt
```

Run the app (must be from the project root — see Imports below):

```bash
.venv/bin/streamlit run app.py
```

The LLM is Google Gemini (`gemini-2.5-flash`) via `langchain-google-genai`, which needs a Gemini API key as the `GOOGLE_API_KEY` environment variable. The key lives in `.env` (gitignored — do not commit it). `app.py` calls `load_dotenv()` at startup, so the variables in `.env` are loaded into the environment before `build_cv_evaluator()` instantiates the Gemini client — no manual `export` needed.

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
