"""
spaced_repetition.py
A lightweight implementation of the SM-2 spaced repetition algorithm
(the same core algorithm behind Anki/SuperMemo) to schedule flashcard review.

Each flashcard gets scheduling metadata:
    - ease_factor: how "easy" the card is (starts at 2.5)
    - interval_days: days until next review
    - repetitions: consecutive correct recalls
    - next_review: date string (ISO) of next due review

Grading scale used here (simplified from SM-2's 0-5 scale to a 3-button UI):
    0 = "Again"  (forgot / wrong)   -> quality 2
    1 = "Hard"   (correct, struggled) -> quality 3
    2 = "Good"   (correct, easy)    -> quality 5
"""

from datetime import date, timedelta

QUALITY_MAP = {"again": 2, "hard": 3, "good": 5}


def init_card_state() -> dict:
    """Default scheduling state for a brand-new flashcard."""
    return {
        "ease_factor": 2.5,
        "interval_days": 0,
        "repetitions": 0,
        "next_review": date.today().isoformat(),
    }


def review_card(card_state: dict, grade: str) -> dict:
    """
    Updates a card's scheduling state based on a review grade.

    Args:
        card_state: dict with keys ease_factor, interval_days, repetitions, next_review
        grade: one of "again", "hard", "good"

    Returns:
        Updated card_state dict
    """
    quality = QUALITY_MAP.get(grade, 3)
    ease = card_state.get("ease_factor", 2.5)
    reps = card_state.get("repetitions", 0)
    interval = card_state.get("interval_days", 0)

    if quality < 3:
        # Forgotten: reset repetitions, review again soon
        reps = 0
        interval = 1
    else:
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 6
        else:
            interval = round(interval * ease)
        reps += 1

    # Update ease factor (SM-2 formula), floor at 1.3
    ease = ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    ease = max(1.3, ease)

    next_review = (date.today() + timedelta(days=interval)).isoformat()

    return {
        "ease_factor": round(ease, 3),
        "interval_days": interval,
        "repetitions": reps,
        "next_review": next_review,
    }


def is_due(card_state: dict) -> bool:
    """True if a card is due for review today or earlier."""
    return date.fromisoformat(card_state["next_review"]) <= date.today()


def get_due_cards(flashcards: list[dict]) -> list[dict]:
    """
    Filters a list of flashcards (each containing a 'srs' sub-dict) down to
    those due for review today.
    """
    return [c for c in flashcards if is_due(c.get("srs", init_card_state()))]
