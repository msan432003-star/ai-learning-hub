"""
llm_engine.py
Core GenAI engine: prompt chaining + structured JSON outputs.
Configured with exponential retry backoffs to absorb 429 rate limits.
"""

import json
import re
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

MODEL_NAME = "gemini-flash-latest"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

DIFFICULTY_GUIDANCE = {
    "Beginner": (
        "Focus on core definitions and foundational concepts. Questions should "
        "test basic recall and simple understanding. Avoid tricky wording."
    ),
    "Exam-Level": (
        "Write questions at the level of a university exam. Test applied "
        "understanding, not just memorization. Include some questions that "
        "require connecting two related concepts."
    ),
    "Tricky Edge Cases": (
        "Write challenging questions that probe common misconceptions, edge "
        "cases, and subtle distinctions an expert would care about."
    ),
}


def _get_client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key, base_url=GEMINI_BASE_URL)


def _extract_json(raw_text: str):
    """Strips markdown code fences and parses JSON robustly."""
    cleaned = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)


# Added reraise=True so RateLimitError passes through cleanly to app.py
@retry(reraise=True, stop=stop_after_attempt(5), wait=wait_exponential(multiplier=3, min=4, max=60))
def _call_llm(api_key: str, system_prompt: str, user_prompt: str, json_mode: bool = True) -> str:
    client = _get_client(api_key)
    kwargs = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.4,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


def summarize_text(api_key: str, text: str, style: str = "Structured Notes") -> str:
    system_prompt = (
        "You are an expert study-notes writer. Turn raw material into clear, "
        "well-organized study notes with headings, bullet points, and bold key terms."
    )
    style_instructions = {
        "Structured Notes": "Produce notes with clear headings (##) per topic and sub-bullets.",
        "Bullet Points": "Produce a flat, concise bulleted list of the most important points only.",
        "TL;DR (short)": "Produce a single short paragraph (under 100 words) capturing the essence.",
    }
    user_prompt = f"{style_instructions.get(style, style_instructions['Structured Notes'])}\n\nSOURCE MATERIAL:\n{text}"
    return _call_llm(api_key, system_prompt, user_prompt, json_mode=False)


def merge_chunk_summaries(api_key: str, chunk_summaries: list[str]) -> str:
    system_prompt = (
        "You are an expert editor. Merge the following partial summaries into a "
        "single coherent, non-repetitive set of study notes with clear headings."
    )
    joined = "\n\n---SECTION BREAK---\n\n".join(chunk_summaries)
    return _call_llm(api_key, system_prompt, f"PARTIAL SUMMARIES:\n{joined}", json_mode=False)


def generate_flashcards(api_key: str, text: str, num_cards: int = 10, difficulty: str = "Exam-Level") -> list[dict]:
    system_prompt = (
        "You are an expert flashcard writer. Each flashcard tests ONE atomic concept. "
        f"Difficulty: {difficulty}. {DIFFICULTY_GUIDANCE[difficulty]}\n\n"
        "Respond ONLY with valid JSON in this exact shape:\n"
        '{"flashcards": [{"question": "...", "answer": "...", "topic": "..."}]}'
    )
    user_prompt = f"Generate exactly {num_cards} flashcards from this material:\n\n{text}"
    raw = _call_llm(api_key, system_prompt, user_prompt, json_mode=True)
    parsed = _extract_json(raw)
    return parsed.get("flashcards", [])


def generate_quiz(api_key: str, text: str, num_questions: int = 5, difficulty: str = "Exam-Level") -> list[dict]:
    system_prompt = (
        "You are an expert exam question writer. Create multiple-choice questions "
        "with exactly 4 options (A-D) and one correct answer. "
        f"Difficulty: {difficulty}. {DIFFICULTY_GUIDANCE[difficulty]}\n\n"
        "Respond ONLY with valid JSON in this exact shape:\n"
        '{"quiz": [{"question": "...", "options": {"A": "...", "B": "...", '
        '"C": "...", "D": "..."}, "correct_option": "A", '
        '"explanation": "short reason", "topic": "..."}]}'
    )
    user_prompt = f"Generate exactly {num_questions} multiple-choice questions from this material:\n\n{text}"
    raw = _call_llm(api_key, system_prompt, user_prompt, json_mode=True)
    parsed = _extract_json(raw)
    return parsed.get("quiz", [])


def explain_mistake(api_key: str, question: str, options: dict, correct_option: str,
                     user_option: str, source_context: str = "") -> str:
    system_prompt = (
        "You are a patient AI tutor. Explain step-by-step why the student's answer "
        "was wrong and why the correct answer is right. Keep it under 180 words."
    )
    user_prompt = (
        f"Question: {question}\n"
        f"Options: {json.dumps(options)}\n"
        f"Student answer: {user_option}\n"
        f"Correct answer: {correct_option}\n"
        f"Context: {source_context[:2000]}"
    )
    return _call_llm(api_key, system_prompt, user_prompt, json_mode=False)