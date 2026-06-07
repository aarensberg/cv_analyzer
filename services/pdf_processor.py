"""extracts text from the uploaded PDF"""

import PyPDF2
from io import BytesIO

# Any return value of extract_pdf_text() that starts with this prefix signals a
# failure (image-only/scanned PDF or an unreadable file) rather than CV text, so
# the UI can detect the problem and react instead of sending junk to the LLM.
PDF_ERROR_PREFIX = "⚠️"

PDF_EXTRACTION_ERROR = (
    f"{PDF_ERROR_PREFIX} No selectable text could be extracted from this PDF. "
    "It looks like a scanned or image-only document — please upload a text-based PDF."
)


def extract_pdf_text(uploaded_file) -> str:
    """Reads an uploaded PDF and returns its concatenated text.

    On success, returns the text of all pages joined by blank lines. On failure
    (no selectable text, or an unreadable/corrupt file) returns an error string
    that starts with ``PDF_ERROR_PREFIX`` so the caller can detect it.
    """
    try:
        # Streamlit's UploadedFile is a file-like object; wrap its bytes in
        # BytesIO so PyPDF2 can seek through them.
        pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))

        pages_text = []
        for page in pdf_reader.pages:
            text = page.extract_text()
            # Skip pages that hold no selectable text (e.g. image-only pages).
            if text and text.strip():
                pages_text.append(text.strip())

        if not pages_text:
            return PDF_EXTRACTION_ERROR

        return "\n\n".join(pages_text)

    except Exception as exc:  # corrupt file, not a PDF, encrypted, etc.
        return f"{PDF_ERROR_PREFIX} Could not read the PDF file ({exc}). Please upload a valid PDF."
