"""Adim 5: 45-80 yas kitlesi icin yuksek kontrastli, buyuk fontlu kapak."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

YELLOW = (255, 214, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 16, 16)


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default(size=size)


def make_thumbnail(image: Path, text: str, out: Path, font_path: str) -> Path:
    W, H = 1280, 720
    img = Image.open(image).convert("RGB")
    scale = max(W / img.width, H / img.height)
    img = img.resize((int(img.width * scale) + 1, int(img.height * scale) + 1))
    left, top = (img.width - W) // 2, (img.height - H) // 2
    img = img.crop((left, top, left + W, top + H))
    img = ImageEnhance.Contrast(img).enhance(1.25)

    # Sol alt tarafi karart, metin okunsun.
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rectangle((0, H * 0.45, W, H), fill=(0, 0, 0, 150))
    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(img)

    words = text.upper().split()
    lines = [" ".join(words[:2]), " ".join(words[2:])] if len(words) > 2 else [" ".join(words)]
    lines = [l for l in lines if l]
    size = 150
    font = _font(font_path, size)
    while any(draw.textlength(l, font=font) > W - 120 for l in lines) and size > 70:
        size -= 8
        font = _font(font_path, size)

    y = H - 60 - len(lines) * (size + 14)
    for i, line in enumerate(lines):
        color = YELLOW if i == len(lines) - 1 else WHITE
        draw.text((60, y), line, font=font, fill=color, stroke_width=10, stroke_fill=BLACK)
        y += size + 14

    draw.rectangle((0, 0, 28, H), fill=RED)
    img.convert("RGB").save(out, "JPEG", quality=92)
    return out
