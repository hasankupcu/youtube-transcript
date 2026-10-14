"""Adim 2: ElevenLabs veya Fish Audio ile seslendirme."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import requests

from ..config import env


def _elevenlabs(text: str, voice_id: str, out: Path) -> None:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": env("ELEVENLABS_API_KEY", required=True), "accept": "audio/mpeg"}
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.55, "similarity_boost": 0.8, "style": 0.2},
    }
    r = requests.post(url, headers=headers, json=payload, timeout=600)
    r.raise_for_status()
    out.write_bytes(r.content)


def _fish(text: str, reference_id: str, out: Path) -> None:
    url = "https://api.fish.audio/v1/tts"
    headers = {"Authorization": f"Bearer {env('FISH_AUDIO_API_KEY', required=True)}"}
    payload = {"text": text, "reference_id": reference_id, "format": "mp3", "normalize": True}
    r = requests.post(url, headers=headers, json=payload, timeout=600)
    r.raise_for_status()
    out.write_bytes(r.content)


def audio_duration(path: Path) -> float:
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(path)]
    info = json.loads(subprocess.check_output(cmd))
    return float(info["format"]["duration"])


def synthesize(channel: dict, narration: str, out: Path) -> float:
    provider = channel["tts_provider"]
    if provider == "elevenlabs":
        _elevenlabs(narration, channel["voice_id"], out)
    elif provider == "fish":
        _fish(narration, channel["voice_id"], out)
    else:
        raise ValueError(f"Bilinmeyen tts_provider: {provider}")
    return audio_duration(out)
