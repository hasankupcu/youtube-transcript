"""Telegram ile onay bildirimi. Token yoksa sessizce gecer."""
from __future__ import annotations

from pathlib import Path

import requests

from ..config import env


def send(text: str, photo: Path | None = None) -> None:
    token, chat = env("TELEGRAM_BOT_TOKEN"), env("TELEGRAM_CHAT_ID")
    if not token or not chat:
        return
    base = f"https://api.telegram.org/bot{token}"
    try:
        if photo and photo.exists():
            with open(photo, "rb") as f:
                requests.post(f"{base}/sendPhoto", data={"chat_id": chat, "caption": text[:1000]},
                              files={"photo": f}, timeout=60)
        else:
            requests.post(f"{base}/sendMessage", data={"chat_id": chat, "text": text[:4000]}, timeout=60)
    except requests.RequestException:
        pass
