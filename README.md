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

## Testing it

Per the brief, try at least three CVs against at least two job descriptions:

- A CV that is a clear strong match → expect a high `fit_percentage`.
- A CV from a different field → watch the fit percentage drop.
- A CV with little experience → watch the strengths / areas-for-improvement shift.

The structured object always parses, even when the PDF text is messy; an
image-only (scanned) PDF is detected and reported instead of being sent to the LLM.

## Reflections

**Why split the app into modules instead of one `app.py`?** Each module has a
single responsibility, so the schema, prompts, PDF handling, LLM logic, and UI
can be read, tested, and changed in isolation. The services never import
Streamlit, so the core logic could be reused behind a CLI or API.

**Why careful `description=` on each `Field`?** With structured output the
descriptions *are* the instructions — they are sent to the model as the schema
contract. A vague description gives vague extraction; a precise one (e.g. "5 to
7 skills most relevant to the role") steers the model directly.

**Why keep the persona in the system message?** It sets stable, role-level
context (who the model is, what criteria and tone to use) separately from the
per-request data (this CV, this job), which keeps the human message focused and
the behavior consistent across calls.

**What problems disappear with `with_structured_output()`?** No prompt-engineered
JSON, no brittle string/JSON parsing, no "the model added prose around the JSON"
failures. The result is a validated Pydantic object with full type safety — the
fit percentage is guaranteed to be an int in 0–100, or the call fails loudly.

**What if the PDF is a scanned image?** `extract_pdf_text` returns a clear error
string (prefixed with a sentinel) so the UI can detect it and ask for a
text-based PDF instead of sending empty text to the LLM.

**What does the UI do while the LLM works?** It shows a spinner during PDF
extraction and during generation so the user knows the app is busy.

### Where to go next

- **Caching:** wrap `evaluate_candidate` (or the chain build) with caching keyed
  on `(cv_text, job_description)` so re-analyzing the same CV doesn't call the LLM
  twice. `build_cv_evaluator()` could also be cached so the client is built once.
- **Other languages:** the prompts work across languages, but you could detect
  the CV's language and instruct the model to answer in a chosen output language.
- **Hiring-committee memo:** add a second LLM call that takes the structured
  `CVAnalysis` and drafts a one-paragraph memo to the recruiter.
