"""Adim 6: YouTube Data API v3 ile yukle, private + publishAt ile zamanla."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from ..config import ROOT

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube"]


def load_credentials(token_path: str) -> Credentials:
    path = ROOT / token_path
    if not path.exists():
        raise SystemExit(f"Token yok: {path}. Once: python -m pipeline.auth_youtube <kanal>")
    creds = Credentials.from_authorized_user_file(str(path), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        path.write_text(creds.to_json())
    return creds


def next_publish_time(hour_utc: int) -> str:
    now = datetime.now(timezone.utc)
    slot = now.replace(hour=hour_utc, minute=0, second=0, microsecond=0)
    if slot <= now + timedelta(minutes=30):
        slot += timedelta(days=1)
    return slot.strftime("%Y-%m-%dT%H:%M:%SZ")


def upload_video(channel: dict, video: Path, thumbnail: Path, meta: dict,
                 publish_at: str | None = None) -> str:
    youtube = build("youtube", "v3", credentials=load_credentials(channel["youtube_token"]))
    publish_at = publish_at or next_publish_time(int(channel["publish_hour_utc"]))
    body = {
        "snippet": {
            "title": meta["title"][:100],
            "description": meta["description"][:5000],
            "tags": meta["tags"][:30],
            "categoryId": str(channel["category_id"]),
            "defaultLanguage": channel["language"],
            "defaultAudioLanguage": channel["language"],
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at,
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(str(video), chunksize=8 * 1024 * 1024, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        _, response = request.next_chunk()
    video_id = response["id"]
    youtube.thumbnails().set(videoId=video_id, media_body=str(thumbnail)).execute()
    return video_id
