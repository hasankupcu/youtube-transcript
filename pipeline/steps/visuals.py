"""Adim 3: Her sahne icin Pexels'ten yatay fotograf indir.

AI gorsel (Flux, Ideogram vb.) kullanmak istersen fetch_scene_image fonksiyonunu
kendi saglayicinla degistir. Imza ayni kalsin: (query, out_path) -> bool
"""
from __future__ import annotations

from pathlib import Path

import requests
from PIL import Image, ImageDraw

from ..config import env

PEXELS_URL = "https://api.pexels.com/v1/search"


def fetch_scene_image(query: str, out: Path, used_ids: set[int]) -> bool:
    key = env("PEXELS_API_KEY")
    if not key:
        return False
    params = {"query": query, "orientation": "landscape", "per_page": 8, "size": "large"}
    r = requests.get(PEXELS_URL, headers={"Authorization": key}, params=params, timeout=60)
    if r.status_code != 200:
        return False
    for photo in r.json().get("photos", []):
        if photo["id"] in used_ids:
            continue
        img = requests.get(photo["src"]["landscape"], timeout=120)
        if img.status_code == 200:
            out.write_bytes(img.content)
            used_ids.add(photo["id"])
            return True
    return False


def placeholder(out: Path, text: str, size: tuple[int, int]) -> None:
    img = Image.new("RGB", size, (24, 28, 40))
    ImageDraw.Draw(img).text((60, size[1] // 2), text[:80], fill=(220, 220, 220))
    img.save(out)


def fetch_all(scenes: list[dict], folder: Path, size: tuple[int, int]) -> list[Path]:
    folder.mkdir(parents=True, exist_ok=True)
    used: set[int] = set()
    paths = []
    for i, scene in enumerate(scenes, start=1):
        path = folder / f"scene_{i:03d}.jpg"
        if not path.exists() and not fetch_scene_image(scene["image_query"], path, used):
            placeholder(path, scene["image_query"], size)
        paths.append(path)
    return paths
