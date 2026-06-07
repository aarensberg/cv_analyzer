# CV Analyzer with Structured Outputs

A modular Streamlit application that uses an LLM (Google Gemini) to analyze a
candidate's CV (PDF) against a specific job description and return a **typed
Pydantic object** — not free-form text — that the UI renders directly.

Course project for *Introduction to Generative AI and LLMs* — Albert School of
Business & Data.

## What it does

1. You upload a CV as a PDF and paste a job description.
2. `PyPDF2` extracts the plain text from the PDF.
3. An LCEL chain (`ChatPromptTemplate | llm.with_structured_output(CVAnalysis)`)
   sends both to `gemini-2.5-flash` and forces the model to answer in the shape
   of the `CVAnalysis` schema.
4. The UI renders the typed result: a fit score, candidate summary, key skills,
   strengths, areas for improvement, and a hire / no-hire recommendation.

## Architecture

Single-responsibility modules with a one-directional data flow:

```
app.py                      # entry point — loads .env, launches the UI
models/cv_model.py          # CVAnalysis — the Pydantic schema the LLM must match
prompts/cv_prompts.py       # system (recruiter persona) + human ({job_description}, {cv_text})
services/pdf_processor.py   # extract_pdf_text(uploaded_file) -> str   (PyPDF2)
services/cv_evaluator.py    # build_cv_evaluator() builds the chain; evaluate_candidate() runs it
ui/streamlit_ui.py          # two-column Streamlit UI + render_results()
```

Flow: UI uploads PDF → `extract_pdf_text` → `evaluate_candidate(cv_text, job_description)`
→ chain `CHAT_PROMPT | base_llm.with_structured_output(CVAnalysis)` → typed
`CVAnalysis` back to the UI.

## Setup & run

```bash
# 1. Install dependencies into the existing virtual environment
.venv/bin/pip install -r requirements.txt

# 2. Provide your Gemini API key (kept out of git)
echo "GOOGLE_API_KEY=your_key_here" > .env

# 3. Run from the project root (imports are absolute from here)
.venv/bin/streamlit run app.py
```

## Test results

The app was run end-to-end against **two real alternance offers** and **three
CVs**. Inputs and outputs live under `tests/` — `tests/first/` = Edmond de
Rothschild *Business AI*, `tests/second/` = Natixis CIB *Data Scientist, Internal
Audit*; the `*.pdf` files are the actual Streamlit result pages. (Personal CVs and
the markdown exports are git-ignored.)

| CV | EdR – Business AI | Natixis – Data Scientist (Audit) |
|---|:---:|:---:|
| Strong match (current CV) | **93 %** · Excellent ✅ | **93 %** · Excellent ✅ |
| Different field (communication) | **8 %** · Low ❌ | **5 %** · Low ❌ |
| Little experience (1st-year CV) | **54 %** · Average 🤔 | **30 %** · Low ❌ |

**Analysis**

- **Scores rank as expected** — strong ≫ junior ≫ off-field — which validates
  `fit_percentage` as a discriminating signal.
- **The evaluation is job-aware**: the same CV yields different gaps per role —
  Databricks is flagged only for EdR (which lists it), internal-audit/CIB
  knowledge only for Natixis, and the junior CV's contract/start-date mismatch is
  caught only against the Natixis offer.
- **Requirements matter**: the junior CV scores lower at Natixis (30 %) than EdR
  (54 %) because Natixis explicitly asks for an MSc + prior IT background, so the
  bachelor-level profile is penalised.
- **Structured output parsed cleanly on all 8 runs**, including French-language
  CVs — the typed `CVAnalysis` contract held up on messy, real-world input.
- **Minor quirks**: `years_of_experience` for the same strong CV came out as 2 vs
  1 across the two roles (read relative to the role, at temperature 0.2), and
  `key_skills` are sometimes echoed in the CV's language (French) while the prose
  stays English — see the multilingual note below.

## Reflections (concise)

- **Why multiple files, not one `app.py`?** Single-responsibility modules are
  easier to test and reuse, and the services never import Streamlit.
- **Why careful `Field(description=...)`?** With structured output the
  descriptions *are* the instructions sent to the model — vague description,
  vague extraction.
- **Why the persona in the system message?** It fixes stable role/tone context,
  separate from the per-request data, so behaviour stays consistent.
- **Pydantic object vs free text?** No JSON parsing, no stray prose, guaranteed
  types (`fit_percentage` is an int 0–100) — or the call fails loudly.
- **Scanned / image-only PDF?** `extract_pdf_text` returns a sentinel-prefixed
  error string the UI detects, so empty text never reaches the LLM.
- **What does the UI show while generating?** Spinners during both PDF extraction
  and LLM generation.
- **`with_structured_output()` vs prompt-and-parse JSON?** The schema is enforced
  and validated automatically — no fragile manual parsing or retry loops.
- **CVs in another language?** Already works (see the French CVs above); to
  control the *output* language, detect the CV's language and instruct the model
  which language to answer in.
- **Where to add caching?** Memoise `evaluate_candidate` keyed on
  `(cv_text, job_description)` (e.g. `st.cache_data`), and build the client once.
- **Add a hiring-committee memo?** Chain a second LLM call that takes the
  `CVAnalysis` object and drafts a one-paragraph memo to the recruiter.
