"""
export_utils.py
Handles exporting flashcards and summaries to portable formats:
  - CSV (compatible with Anki "Basic" note type import, and Quizlet's
    "import from Word/Excel" tab-or-comma-separated flow)
  - PDF summary sheet (formatted study handout)
"""

import pandas as pd
import io
import re
from fpdf import FPDF


def flashcards_to_csv_bytes(flashcards: list[dict]) -> bytes:
    """
    Converts flashcards to CSV bytes ready for download.
    Anki import: File > Import > choose 'Fields separated by: Comma',
    map column 1 -> Front, column 2 -> Back.
    Quizlet import: use 'Import from Word, Excel, Google Docs' and paste
    the CSV content, with "," as term/definition separator and newline
    as card separator.
    """
    df = pd.DataFrame(flashcards)[["question", "answer", "topic"]]
    df.columns = ["Front", "Back", "Topic"]
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


class _StudyPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "AI Learning Hub - Study Summary", ln=True, align="C")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def _break_long_words(text: str, max_word_len: int = 40) -> str:
    def _break(match):
        word = match.group(0)
        return " ".join(word[i:i + max_word_len] for i in range(0, len(word), max_word_len))
    return re.sub(r"\S+", _break, text)


def _sanitize(text: str) -> str:
    """FPDF core fonts only support latin-1; strip/replace unsupported chars,
    and ensure no single word is too wide for the page to wrap."""
    latin1_safe = text.encode("latin-1", "replace").decode("latin-1")
    return _break_long_words(latin1_safe)


def summary_and_flashcards_to_pdf_bytes(summary_text: str, flashcards: list[dict]) -> bytes:
    """
    Builds a formatted PDF containing the study summary followed by a
    flashcard reference sheet (question + answer table).
    """
    pdf = _StudyPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # --- Summary section ---
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_x(pdf.l_margin)
    pdf.cell(0, 8, "Study Notes", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 6, _sanitize(summary_text))
    pdf.ln(4)

    # --- Flashcards section ---
    if flashcards:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_x(pdf.l_margin)
        pdf.cell(0, 8, "Flashcards", ln=True)
        pdf.ln(2)

        for i, card in enumerate(flashcards, 1):
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_x(pdf.l_margin)
            q = _sanitize(f"{i}. {card.get('question', '')}")
            pdf.multi_cell(0, 6, q)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_x(pdf.l_margin)
            a = _sanitize(f"   Answer: {card.get('answer', '')}")
            pdf.multi_cell(0, 6, a)
            pdf.ln(2)

    return bytes(pdf.output(dest="S"))