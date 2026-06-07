"""extracts text from the uploaded PDF"""

import PyPDF2
from io import BytesIO


def extract_pdf_text(uploaded_file) -> str:
    """Reads an uploaded PDF and returns its concatenated text."""
    # Hints:
    # - Wrap uploaded_file.read() in BytesIO before passing to PyPDF2.PdfReader
    # - Iterate over pdf_reader.pages and call page.extract_text()
    # - Skip empty pages and join the rest with newlines
    # - Return a clear error string if nothing was extracted (image-only PDFs)
    ...
