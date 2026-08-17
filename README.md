🧠 AI Learning Hub — Smart Study Notes, Flashcards & Quizzes

A personalized AI-powered study companion built with Streamlit + Google Gemini. Upload text, PDFs, or paste your notes and get structured summaries, active-recall flashcards, difficulty-tiered quizzes, an "Explain My Mistakes" AI tutor, spaced-repetition scheduling (SM-2), and one-click export to Anki/Quizlet CSV or PDF.

<!-- 💡 TIP: Add a screenshot or short GIF demo here — it's the single biggest thing that makes a README convincing at a glance. Example: ![App demo](docs/demo.gif) -->

Show Image Show Image Show Image

✨ Features
Feature	Description
📄 Multi-input ingestion	Paste text or upload a PDF and get instantly parsed, chunked content ready for processing
📝 Structured summarization	Choose Structured Notes / Bullet Points / TL;DR — auto-chunks long documents
🎴 Active recall flashcards	Self-test UI: type your answer, reveal, then grade yourself
⏱️ Spaced repetition (SM-2)	Same core algorithm as Anki — cards you know well show up less often
🧩 Interactive quiz mode	Multiple-choice with immediate feedback and a running score
🎚️ Difficulty tiers	Beginner / Exam-Level / Tricky Edge Cases — controls prompt complexity
🧑‍🏫 "Explain My Mistakes" tutor	Step-by-step, chain-of-thought explanation for any wrong answer
📤 Export	Download flashcards as Anki/Quizlet-ready CSV, or a formatted PDF study sheet
🛠️ Tech Stack
Frontend: Streamlit
GenAI Engine: Google Gemini API (gemini-2.0-flash, free tier) via its OpenAI-compatible endpoint — used for structured JSON outputs and prompt chaining
Data Ingestion: pypdf for PDF text extraction, native text input
Export: pandas (CSV), fpdf2 (PDF)
Hosting: Streamlit Community Cloud or AWS EC2

Note: Audio lecture upload/transcription (via Whisper) is planned but not currently enabled in this configuration. See Roadmap below.

📁 Project Structure
study_hub/
├── app.py                     # Main Streamlit app (UI + orchestration)
├── requirements.txt
├── README.md
└── modules/
    ├── pdf_utils.py           # PDF text extraction + chunking
    ├── audio_utils.py         # Whisper-based audio transcription (not yet wired into app.py)
    ├── llm_engine.py          # All prompts: summarize, flashcards, quiz, tutor
    ├── spaced_repetition.py   # SM-2 scheduling algorithm
    └── export_utils.py        # CSV + PDF export
🚀 Setup

1. Clone the repo and install dependencies

bash
git clone https://github.com/msan432003-star/ai-learning-hub.git
cd ai-learning-hub
pip install -r requirements.txt

2. Get a free Gemini API key (no credit card required)

Go to aistudio.google.com/apikey
Sign in with Google → Create API key → copy it

3. Set your API key — pick one:

Create a .env file in the project root:
  GEMINI_API_KEY=AIzaSy...
Or export it in your shell:
bash
  export GEMINI_API_KEY=AIzaSy...
Or paste it directly into the sidebar text box once the app is running

4. Run the app

bash
streamlit run app.py

Open the local URL Streamlit prints (usually http://localhost:8501).

🧭 How to Use It
Upload tab — paste notes or upload a PDF
Summary tab — generate structured notes in your preferred style
Flashcards tab — generate flashcards, self-test, and grade yourself (Again / Hard / Good) to build your spaced-repetition schedule. The sidebar shows how many cards are due for review today
Quiz Mode tab — take a difficulty-tiered multiple-choice quiz. Wrong answers show a "🧑‍🏫 Explain Why" button for a step-by-step breakdown
Export tab — download flashcards as CSV (Anki/Quizlet-ready) or a full PDF study sheet
🔑 Importing the CSV into Anki / Quizlet

Anki: File → Import → select flashcards.csv → Fields separated by Comma → map column 1 to Front, column 2 to Back.

Quizlet: Create a new study set → "Import from Word, Excel, Google Docs" → paste the CSV contents → set "Between term and definition" to Comma, "Between cards" to New line.

⚠️ Notes & Limitations
Audio transcription (Whisper) is scaffolded in audio_utils.py but not currently wired into the live app
Scanned/image-only PDFs won't extract text — no OCR built in yet
All quiz/flashcard content is grounded in the uploaded material via prompt instructions, but as with any LLM output, spot-check important facts
Flashcard/quiz data is session-only — refreshing the page clears progress
API usage is subject to Gemini's free-tier rate limits
🗺️ Roadmap
 Wire up audio lecture transcription (Whisper)
 OCR fallback for scanned PDFs (pytesseract)
 Multi-user accounts with persistent flashcard decks (currently session-only)
 Topic-level analytics dashboard (which topics you get wrong most)
 Optional OpenAI backend as an alternative to Gemini
📄 License

This project is licensed under the MIT License.

🙌 Contributing

Issues and pull requests are welcome! If you spot a bug or have a feature idea, feel free to open an issue.
