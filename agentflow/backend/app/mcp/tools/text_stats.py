"""
AgentFlow — MCP Text Stats Tool
Counts characters, words, and sentences in text.
"""
from __future__ import annotations

import re
from typing import Any, Dict


def text_stats(text: str) -> Dict[str, Any]:
    """
    Compute statistics about a piece of text.

    Args:
        text: The text to analyze

    Returns:
        dict with character, word, and sentence counts
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string.")

    text = text.strip()

    # Character count (including spaces)
    char_count = len(text)
    # Character count (excluding spaces)
    char_no_spaces = len(text.replace(" ", ""))

    # Word count — split on whitespace
    words = text.split() if text else []
    word_count = len(words)

    # Sentence count — split on . ! ? followed by whitespace or end
    sentences = re.split(r'(?<=[.!?])\s+|(?<=[.!?])$', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences)

    # Paragraph count
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    paragraph_count = len(paragraphs)

    # Unique word count (case-insensitive)
    unique_words = len(set(w.lower().strip(".,!?;:\"'()[]{}") for w in words))

    # Avg word length
    avg_word_length = (
        round(sum(len(w) for w in words) / word_count, 2) if word_count > 0 else 0.0
    )

    return {
        "characters": char_count,
        "characters_no_spaces": char_no_spaces,
        "words": word_count,
        "unique_words": unique_words,
        "sentences": sentence_count,
        "paragraphs": paragraph_count,
        "avg_word_length": avg_word_length,
    }


TOOL_DEFINITION = {
    "name": "text_stats",
    "description": "Analyze text and return statistics: character count, word count, sentence count, and more.",
    "input_schema": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The text to analyze",
            }
        },
        "required": ["text"],
    },
}
