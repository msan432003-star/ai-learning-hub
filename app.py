"""
app.py
Personalized AI Learning Hub
------------------------------
An AI-powered study assistant: upload notes (text / PDF), get
structured summaries, generate difficulty-tiered flashcards and quizzes,
get step-by-step explanations on mistakes, track review with spaced
repetition, and export everything to Anki/Quizlet CSV or a PDF handout.

Run with:  python -m streamlit run app.py
"""

import os
import time
import streamlit as st
from dotenv import load_dotenv

from modules import pdf_utils, llm_engine, export_utils, spaced_repetition as srs

load_dotenv()

st.set_page_config(
    page_title="AI Learning Hub",
    page_icon="🧠",
    layout="wide",
)

# ---------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------------------------

defaults = {
    "source_text": "",
    "summary": "",
    "flashcards": [],       # list of {question, answer, topic, srs: {...}}
    "quiz": [],             # list of {question, options, correct_option, explanation, topic}
    "quiz_answers": {},     # {question_index: selected_option}
    "quiz_submitted": False,
    "explanations": {},     # {question_index: explanation_text}
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ---------------------------------------------------------------------------
# SIDEBAR — CONFIG & API KEY PROMPT
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🧠 AI Learning Hub")
    st.caption("Personalized study notes, flashcards & quizzes powered by GenAI")

    env_api_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input(
        "Gemini API Key",
        value=env_api_key,
        type="password",
        help="Free, no card required. Get one at aistudio.google.com/apikey",
    )

    if not api_key:
        st.warning("⚠️ **Gemini API Key Required**\nPlease paste your key above to enable AI features. You can get a free key at [aistudio.google.com](https://aistudio.google.com/apikey).")

    st.divider()
    st.subheader("⚙️ Study Settings")
    difficulty = st.select_slider(
        "Difficulty",
        options=["Beginner", "Exam-Level", "Tricky Edge Cases"],
        value="Exam-Level",
    )
    num_flashcards = st.slider("Number of flashcards", 5, 25, 10)
    num_quiz_qs = st.slider("Number of quiz questions", 3, 15, 5)
    summary_style = st.selectbox(
        "Summary style",
        ["Structured Notes", "Bullet Points", "TL;DR (short)"],
    )

    st.divider()
    due_count = len(srs.get_due_cards(st.session_state.flashcards))
    st.metric("Flashcards due for review", due_count)

# ---------------------------------------------------------------------------
# TABS
# ---------------------------------------------------------------------------

tab_upload, tab_summary, tab_flashcards, tab_quiz, tab_export = st.tabs(
    ["📥 Upload", "📝 Summary", "🎴 Flashcards", "🧩 Quiz Mode", "📤 Export"]
)

# ---------------------------------------------------------------------------
# TAB 1: UPLOAD (Text / PDF)
# ---------------------------------------------------------------------------

with tab_upload:
    st.header("Add your study material")
    input_mode = st.radio(
        "Input type", ["📄 Paste Text", "📕 Upload PDF"],
        horizontal=True,
    )

    if input_mode == "📄 Paste Text":
        text_input = st.text_area("Paste your notes here", height=300)
        if st.button("Use this text", type="primary"):
            if text_input.strip():
                st.session_state.source_text = pdf_utils.clean_text_input(text_input)
                st.success(f"Loaded {len(st.session_state.source_text)} characters.")
            else:
                st.warning("Please paste some text first.")

    elif input_mode == "📕 Upload PDF":
        pdf_file = st.file_uploader("Upload a PDF document", type=["pdf"])
        if pdf_file and st.button("Extract text from PDF", type="primary"):
            try:
                with st.spinner("Extracting text from PDF..."):
                    extracted = pdf_utils.extract_text_from_pdf(pdf_file)
                st.session_state.source_text = extracted
                st.success(f"Successfully extracted {len(extracted)} characters from PDF.")
                with st.expander("Preview extracted text"):
                    st.text(extracted[:2000] + ("..." if len(extracted) > 2000 else ""))
            except ValueError as e:
                st.error(f"❌ {str(e)}")

    if st.session_state.source_text:
        st.info(f"✅ Current study material loaded: {len(st.session_state.source_text)} characters")

# ---------------------------------------------------------------------------
# TAB 2: SUMMARY
# ---------------------------------------------------------------------------

with tab_summary:
    st.header("📝 Structured Study Notes")

    if not st.session_state.source_text:
        st.warning("Please add material in the Upload tab first.")
    else:
        if st.button("Generate Summary", type="primary"):
            if not api_key:
                st.error("🔑 Please enter your Gemini API key in the sidebar first.")
            else:
                try:
                    with st.spinner("Analyzing text and generating summary..."):
                        chunks = pdf_utils.chunk_text(st.session_state.source_text)
                        if len(chunks) == 1:
                            summary = llm_engine.summarize_text(api_key, chunks[0], summary_style)
                        else:
                            partials = []
                            for idx, c in enumerate(chunks):
                                partials.append(llm_engine.summarize_text(api_key, c, summary_style))
                                if idx < len(chunks) - 1:
                                    time.sleep(5.0)  # Rate limit pacing
                            summary = llm_engine.merge_chunk_summaries(api_key, partials)
                        st.session_state.summary = summary
                    st.success("Summary generated successfully!")
                except Exception as e:
                    err_msg = str(e).lower()
                    if "429" in err_msg or "resource_exhausted" in err_msg or "ratelimit" in err_msg or "retryerror" in err_msg:
                        st.error(f"⏳ **API Rate Limit Reached**: Google Gemini's free API tier is currently rate-limited. Please wait 30–60 seconds and click again.\n\nDetails: {e}")
                    else:
                        st.error(f"Error generating summary: {e}")

        if st.session_state.summary:
            st.markdown(st.session_state.summary)

# ---------------------------------------------------------------------------
# TAB 3: FLASHCARDS
# ---------------------------------------------------------------------------

with tab_flashcards:
    st.header("🎴 Active Recall Flashcards")

    if not st.session_state.source_text:
        st.warning("Please add material in the Upload tab first.")
    else:
        if st.button("Generate Flashcards", type="primary"):
            if not api_key:
                st.error("🔑 Please enter your Gemini API key in the sidebar first.")
            else:
                try:
                    with st.spinner(f"Creating {num_flashcards} {difficulty}-level flashcards..."):
                        cards = llm_engine.generate_flashcards(
                            api_key, st.session_state.source_text, num_flashcards, difficulty
                        )
                        for c in cards:
                            c["srs"] = srs.init_card_state()
                        st.session_state.flashcards = cards
                    st.success(f"Generated {len(cards)} flashcards!")
                except Exception as e:
                    err_msg = str(e).lower()
                    if "429" in err_msg or "resource_exhausted" in err_msg or "ratelimit" in err_msg or "retryerror" in err_msg:
                        st.error(f"⏳ **API Rate Limit Reached**: Google Gemini's free API tier is currently rate-limited. Please wait 30–60 seconds and click again.\n\nDetails: {e}")
                    else:
                        st.error(f"Error generating flashcards: {e}")

        if st.session_state.flashcards:
            st.subheader(f"Review your {len(st.session_state.flashcards)} flashcards")
            st.caption("Try to recall the answer before revealing it, then grade yourself for spaced repetition scheduling.")

            for i, card in enumerate(st.session_state.flashcards):
                with st.expander(f"**Q{i+1}. {card['question']}**  ·  _{card.get('topic', '')}_"):
                    user_recall = st.text_input("Type your answer (optional self-check):", key=f"recall_{i}")
                    reveal = st.button("Reveal Answer", key=f"reveal_{i}")
                    if reveal or user_recall:
                        st.markdown(f"Answer:")

                        grade_cols = st.columns(3)
                        for label, grade_key, col in zip(
                            ["😵 Again", "😐 Hard", "😄 Good"],
                            ["again", "hard", "good"],
                            grade_cols,
                        ):
                            if col.button(label, key=f"grade_{grade_key}_{i}"):
                                st.session_state.flashcards[i]["srs"] = srs.review_card(
                                    card["srs"], grade_key
                                )
                                st.toast(f"Next review: {st.session_state.flashcards[i]['srs']['next_review']}")

# ---------------------------------------------------------------------------
# TAB 4: QUIZ MODE
# ---------------------------------------------------------------------------

with tab_quiz:
    st.header("🧩 Interactive Quiz Mode")

    if not st.session_state.source_text:
        st.warning("Please add material in the Upload tab first.")
    else:
        if st.button("Generate New Quiz", type="primary"):
            if not api_key:
                st.error("🔑 Please enter your Gemini API key in the sidebar first.")
            else:
                try:
                    with st.spinner(f"Creating a {difficulty} quiz..."):
                        quiz = llm_engine.generate_quiz(
                            api_key, st.session_state.source_text, num_quiz_qs, difficulty
                        )
                        st.session_state.quiz = quiz
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_submitted = False
                        st.session_state.explanations = {}
                    st.success(f"Generated a {len(quiz)}-question quiz!")
                except Exception as e:
                    err_msg = str(e).lower()
                    if "429" in err_msg or "resource_exhausted" in err_msg or "ratelimit" in err_msg or "retryerror" in err_msg:
                        st.error(f"⏳ **API Rate Limit Reached**: Google Gemini's free API tier is currently rate-limited. Please wait 30–60 seconds and click again.\n\nDetails: {e}")
                    else:
                        st.error(f"Error generating quiz: {e}")

        if st.session_state.quiz:
            for i, q in enumerate(st.session_state.quiz):
                st.markdown(f"**Q{i+1}. {q['question']}**")
                options = q["options"]
                choice = st.radio(
                    "Select your answer:",
                    options=list(options.keys()),
                    format_func=lambda k, opts=options: f"{k}) {opts[k]}",
                    key=f"quiz_choice_{i}",
                    index=None,
                )
                if choice:
                    st.session_state.quiz_answers[i] = choice
                st.divider()

            if st.button("Submit Quiz", type="primary"):
                st.session_state.quiz_submitted = True

            if st.session_state.quiz_submitted:
                correct_count = 0
                st.subheader("Results")
                for i, q in enumerate(st.session_state.quiz):
                    user_ans = st.session_state.quiz_answers.get(i)
                    correct = q["correct_option"]
                    is_correct = user_ans == correct
                    correct_count += int(is_correct)

                    if is_correct:
                        st.success(f"Q{i+1}: Correct! ({correct}) {q['options'][correct]}")
                    else:
                        st.error(
                            f"Q{i+1}: You chose {user_ans or 'nothing'} — "
                            f"Correct answer is {correct}) {q['options'][correct]}"
                        )
                        st.caption(q.get("explanation", ""))

                        if st.button(f"🧑‍🏫 Explain Why (Q{i+1})", key=f"explain_{i}"):
                            if not api_key:
                                st.error("🔑 Please enter your Gemini API key in the sidebar first.")
                            else:
                                try:
                                    with st.spinner("Thinking through the concept..."):
                                        explanation = llm_engine.explain_mistake(
                                            api_key,
                                            q["question"],
                                            q["options"],
                                            correct,
                                            user_ans or "N/A",
                                            st.session_state.source_text,
                                        )
                                        st.session_state.explanations[i] = explanation
                                except Exception as e:
                                    st.error(f"Error getting explanation: {e}")

                        if i in st.session_state.explanations:
                            st.info(st.session_state.explanations[i])

                st.metric("Score", f"{correct_count} / {len(st.session_state.quiz)}")

# ---------------------------------------------------------------------------
# TAB 5: EXPORT
# ---------------------------------------------------------------------------

with tab_export:
    st.header("📤 Export your study materials")

    if not st.session_state.flashcards and not st.session_state.summary:
        st.warning("Generate a summary and/or flashcards first.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Flashcards → CSV")
            st.caption("Compatible with Anki and Quizlet.")
            if st.session_state.flashcards:
                csv_bytes = export_utils.flashcards_to_csv_bytes(st.session_state.flashcards)
                st.download_button(
                    "⬇️ Download Flashcards CSV",
                    data=csv_bytes,
                    file_name="flashcards.csv",
                    mime="text/csv",
                )
            else:
                st.caption("No flashcards generated yet.")

        with col2:
            st.subheader("Summary + Flashcards → PDF")
            st.caption("Download a formatted study sheet.")
            if st.session_state.summary or st.session_state.flashcards:
                pdf_bytes = export_utils.summary_and_flashcards_to_pdf_bytes(
                    st.session_state.summary or "(No summary generated yet.)",
                    st.session_state.flashcards,
                )
                st.download_button(
                    "⬇️ Download PDF Summary Sheet",
                    data=pdf_bytes,
                    file_name="study_summary.pdf",
                    mime="application/pdf",
                )