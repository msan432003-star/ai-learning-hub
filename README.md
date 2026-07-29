# 🧠 AI Learning Hub — Smart Study Notes, Flashcards & Quizzes

A Personalized AI Learning Hub built with Streamlit + OpenAI. Upload text, PDFs,
or audio lectures, and get structured summaries, active-recall flashcards,
difficulty-tiered quizzes, an "Explain My Mistakes" AI tutor, spaced-repetition
review scheduling (SM-2), and one-click export to Anki/Quizlet CSV or PDF.

## ✨ Features

| Feature | Description |
|---|---|
| 📄 Multi-input ingestion | Paste text, upload a PDF, or upload/record audio (lecture transcription via Whisper) |
| 📝 Structured summarization | Choose Structured Notes / Bullet Points / TL;DR, auto-chunks long documents |
| 🎴 Active recall flashcards | Self-test UI: type your answer, reveal, then grade yourself |
| ⏱️ Spaced repetition (SM-2) | Same core algorithm as Anki — cards you know well show up less often |
| 🧩 Interactive quiz mode | Multiple-choice with immediate feedback and a running score |
| 🎚️ Difficulty tiers | Beginner / Exam-Level / Tricky Edge Cases, controls prompt complexity |
| 🧑‍🏫 "Explain My Mistakes" tutor | Step-by-step, chain-of-thought explanation for any wrong answer |
| 📤 Export | Download flashcards as Anki/Quizlet-ready CSV, or a formatted PDF study sheet |

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **GenAI Engine:** Google Gemini API (`gemini-2.0-flash`, free tier, accessed via its OpenAI-compatible endpoint) — structured JSON outputs + prompt chaining. Audio transcription (Whisper) is disabled in this configuration.
- **Data Ingestion:** `pypdf` for PDFs, native text input, Whisper for audio
- **Export:** `pandas` (CSV), `fpdf2` (PDF)
- **Hosting:** Streamlit Community Cloud or AWS EC2

## 📁 Project Structure

```
study_hub/
├── app.py                     # Main Streamlit app (UI + orchestration)
├── requirements.txt
├── README.md
└── modules/
    ├── pdf_utils.py           # PDF text extraction + chunking
    ├── audio_utils.py         # Whisper-based audio transcription
    ├── llm_engine.py          # All prompts: summarize, flashcards, quiz, tutor
    ├── spaced_repetition.py   # SM-2 scheduling algorithm
    └── export_utils.py        # CSV + PDF export
```

## 🚀 Setup

1. **Clone and install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get a free Gemini API key** (no credit card required):
   - Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
   - Sign in with Google → Create API key → copy it
   - Then either:
     - Create a `.env` file: `GEMINI_API_KEY=AIzaSy...`
     - Or export it: `export GEMINI_API_KEY=AIzaSy...`
     - Or paste it directly into the sidebar text box when the app is running

3. **Run the app:**
   ```bash
   streamlit run app.py
   ```

4. Open the local URL Streamlit prints (usually `http://localhost:8501`).

## 🧭 How to use it

1. **Upload tab** — paste notes, upload a PDF, or upload a lecture recording.
2. **Summary tab** — generate structured notes in your preferred style.
3. **Flashcards tab** — generate flashcards, self-test, and grade yourself
   (Again / Hard / Good) to build your spaced-repetition schedule. The sidebar
   shows how many cards are due for review today.
4. **Quiz Mode tab** — take a difficulty-tiered multiple-choice quiz. Wrong
   answers show a **"🧑‍🏫 Explain Why"** button for a step-by-step breakdown.
5. **Export tab** — download flashcards as CSV (Anki/Quizlet-ready) or a full
   PDF study sheet.

## 🔑 Importing the CSV into Anki / Quizlet

- **Anki:** File → Import → select `flashcards.csv` → Fields separated by
  Comma → map column 1 to *Front*, column 2 to *Back*.
- **Quizlet:** Create a new study set → "Import from Word, Excel, Google Docs"
  → paste the CSV contents → set "Between term and definition" to Comma,
  "Between cards" to New line.

## ⚠️ Notes & Limitations

- Whisper audio transcription has a 25MB file size limit per the OpenAI API.
- Scanned/image-only PDFs won't extract text (no OCR built in) — a good
  next step would be adding `pytesseract` for OCR fallback.
- All quiz/flashcard content is grounded in the uploaded material via prompt
  instructions, but as with any LLM output, spot-check important facts.
- API costs are your own (pay-as-you-go via your OpenAI key).

## 🗺️ Possible Future Extensions

- OCR fallback for scanned PDFs
- Multi-user accounts with persistent flashcard decks (currently session-only)
- Topic-level analytics dashboard (which topics you get wrong most)
- Support for Google Gemini as an alternative backend
