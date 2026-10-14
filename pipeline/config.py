"""Ortak ayarlar: .env, channels.yaml, kuyruk ve is klasorleri."""
from __future__ import annotations

import csv
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

QUEUE_PATH = ROOT / "queue.csv"
OUTPUT_DIR = ROOT / "output"
QUEUE_FIELDS = ["id", "channel", "topic", "angle", "status", "video_id", "notes"]


def env(name: str, required: bool = False) -> str:
    value = os.environ.get(name, "").strip()
    if required and not value:
        raise SystemExit(f"{name} eksik. pipeline/.env dosyasina ekle.")
    return value


def load_channels() -> tuple[dict, dict]:
    with open(ROOT / "channels.yaml", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    defaults = data.get("defaults", {})
    channels = {}
    for key, cfg in data["channels"].items():
        merged = dict(defaults)
        merged.update(cfg)
        merged["key"] = key
        channels[key] = merged
    return defaults, channels


def read_queue() -> list[dict]:
    if not QUEUE_PATH.exists():
        return []
    with open(QUEUE_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_queue(rows: list[dict]) -> None:
    with open(QUEUE_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=QUEUE_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in QUEUE_FIELDS})


def update_queue_row(job_id: str, **fields) -> None:
    rows = read_queue()
    for row in rows:
        if row["id"] == job_id:
            row.update(fields)
    write_queue(rows)


def job_dir(job_id: str) -> Path:
    path = OUTPUT_DIR / f"job_{job_id}"
    path.mkdir(parents=True, exist_ok=True)
    return path
