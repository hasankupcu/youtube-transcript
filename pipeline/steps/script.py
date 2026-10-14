"""Adim 1: Claude ile seslendirmeye hazir, sahnelere bolunmus script uret."""
from __future__ import annotations

import json

import anthropic

SYSTEM_PROMPT = """You write voice-over scripts for faceless YouTube channels aimed at viewers aged 45 to 80.
The video shows many still images that are not synced to the voice. The voice carries everything.

Hard rules for the narration text (it goes straight into ElevenLabs or Fish Audio):
- Write only in {language_name}.
- Short sentences. One idea per sentence. Natural spoken rhythm.
- No parentheses, no brackets, no quotation marks, no dashes, no asterisks, no emojis, no special characters.
- Control pace with full stops and commas only.
- No headings, no labels, no stage directions, no timestamps. Nothing that is not meant to be spoken.

Retention structure you must follow:
- Open with a Zeigarnik hook: raise a specific unresolved question or promise in the first three sentences, and do not resolve it until near the end.
- Build emotional tension loops: open a small question, answer it, and open the next one before the viewer can leave. Every 60 to 90 seconds of speech re-open tension.
- Speak to one person, warmly, like a trusted friend of their generation. Respect their life experience. Never talk down.
- Place exactly one soft call to action around 20 percent of the way in, asking them to tell their own experience in the comments. Place the subscribe ask only after the main promise is paid off, near the end.
- End by resolving the hook, then one line that opens a new loop toward a next video.

Length target: about {target_words} words of narration in total.
Split the narration into scenes of roughly {scene_seconds} seconds of speech each, about {scene_words} words per scene.
For every scene give an image search query in English (3 to 6 words, concrete, photographic, no people's faces in close up) that fits the mood of that scene.
Title: under 60 characters, in {language_name}, curiosity driven, no clickbait lies.
Thumbnail text: 2 to 4 words, in {language_name}, capital letters, emotional.
Description: 3 short paragraphs in {language_name}, no links.
Tags: 12 to 18 short keywords in {language_name}.
"""

SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "thumbnail_text": {"type": "string"},
        "description": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "narration": {"type": "string"},
                    "image_query": {"type": "string"},
                },
                "required": ["narration", "image_query"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["title", "thumbnail_text", "description", "tags", "scenes"],
    "additionalProperties": False,
}

FORBIDDEN = "()[]{}\"*<>#_~|\\"


def _clean_narration(text: str) -> str:
    text = text.replace("—", ", ").replace("–", ", ").replace("-", " ")
    for ch in FORBIDDEN:
        text = text.replace(ch, "")
    return " ".join(text.split())


def generate_script(channel: dict, topic: str, angle: str) -> dict:
    client = anthropic.Anthropic()
    words_per_minute = 140
    target_words = int(channel["target_minutes"] * words_per_minute)
    scene_seconds = int(channel["seconds_per_scene"])
    scene_words = int(scene_seconds * words_per_minute / 60)

    system = SYSTEM_PROMPT.format(
        language_name=channel["language_name"],
        target_words=target_words,
        scene_seconds=scene_seconds,
        scene_words=scene_words,
    )
    user = f"Topic: {topic}\nAngle or story frame: {angle or 'choose the most emotionally resonant angle'}"

    with client.messages.stream(
        model=channel["script_model"],
        max_tokens=32000,
        system=system,
        messages=[{"role": "user", "content": user}],
        output_config={
            "effort": "high",
            "format": {"type": "json_schema", "schema": SCHEMA},
        },
    ) as stream:
        response = stream.get_final_message()

    if response.stop_reason == "refusal":
        raise RuntimeError("Model konuyu reddetti, baska konu sec.")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Script yarim kaldi, max_tokens yukselt.")

    text = next(b.text for b in response.content if b.type == "text")
    data = json.loads(text)
    for scene in data["scenes"]:
        scene["narration"] = _clean_narration(scene["narration"])
    data["narration"] = "\n\n".join(s["narration"] for s in data["scenes"])
    data["word_count"] = len(data["narration"].split())
    return data
