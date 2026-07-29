"""
pdf_utils.py
Handles ingestion of study material: PDFs and raw text.
Includes validation for scanned/empty PDFs.
"""

import io
from pypdf import PdfReader


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extracts raw text from an uploaded PDF file.
    Includes check for scanned/image-only PDFs.
    """
    reader = PdfReader(io.BytesIO(uploaded_file.read()))
    pages_text = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages_text.append(f"[Page {i + 1}]\n{text.strip()}")

    full_text = "\n\n".join(pages_text).strip()

    # Risk 4 Fix: Check for scanned / non-extractable text
    if len(full_text) < 20:
        raise ValueError(
            "Could not extract readable text from this PDF. "
            "It appears to be a scanned document or image-only PDF. "
            "Please paste the text manually or use a text-based PDF."
        )

    return full_text


def chunk_text(text: str, max_chars: int = 12000) -> list[str]:
    """Splits large text into chunks for LLM context limits."""
    if len(text) <= max_chars:
        return [text]

    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 <= max_chars:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            if len(para) > max_chars:
                for i in range(0, len(para), max_chars):
                    chunks.append(para[i:i + max_chars])
                current_chunk = ""
            else:
                current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def clean_text_input(raw_text: str) -> str:
    """Basic cleanup for pasted text input."""
    lines = [line.rstrip() for line in raw_text.splitlines()]
    cleaned = "\n".join(line for line in lines if line.strip() != "")
    return cleaned.strip()