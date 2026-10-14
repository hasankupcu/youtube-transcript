"""Gunluk orkestrator.

  python -m pipeline.run_daily render --channel fr      # kuyruktan ilk bekleyeni uret, onaya gonder
  python -m pipeline.run_daily upload --job 1           # onaylanan isi yukle ve zamanla
  python -m pipeline.run_daily auto --channel fr        # uret + yukle (onay kapisi yok)
  python -m pipeline.run_daily auto --all               # butun kanallar icin auto

Her is pipeline/output/job_<id>/ altinda saklanir: script.json, voice.mp3,
images/, video.mp4, thumbnail.jpg. Bir adim bittiyse tekrar calistirmada atlanir.
"""
from __future__ import annotations

import argparse
import json
import sys
import traceback

from .config import job_dir, load_channels, read_queue, update_queue_row
from .steps import assemble, notify, script, thumbnail, tts, upload, visuals


def pick_job(channel_key: str) -> dict | None:
    for row in read_queue():
        if row["channel"] == channel_key and row["status"] == "pending":
            return row
    return None


def render(job: dict, channel: dict) -> dict:
    jd = job_dir(job["id"])
    script_path = jd / "script.json"
    if script_path.exists():
        data = json.loads(script_path.read_text(encoding="utf-8"))
    else:
        print(f"[{job['id']}] script yaziliyor")
        data = script.generate_script(channel, job["topic"], job["angle"])
        script_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        (jd / "narration.txt").write_text(data["narration"], encoding="utf-8")
    print(f"[{job['id']}] {data['word_count']} kelime, {len(data['scenes'])} sahne")

    voice = jd / "voice.mp3"
    if not voice.exists():
        print(f"[{job['id']}] seslendiriliyor ({channel['tts_provider']})")
        tts.synthesize(channel, data["narration"], voice)
    duration = tts.audio_duration(voice)
    print(f"[{job['id']}] ses suresi {duration/60:.1f} dk")

    size = (int(channel["width"]), int(channel["height"]))
    images = visuals.fetch_all(data["scenes"], jd / "images", size)

    video = jd / "video.mp4"
    if not video.exists():
        print(f"[{job['id']}] montaj")
        assemble.build_video(data["scenes"], images, voice, duration, channel, jd, video)

    thumb = jd / "thumbnail.jpg"
    if not thumb.exists():
        thumbnail.make_thumbnail(images[0], data["thumbnail_text"], thumb, channel["thumbnail_font"])

    update_queue_row(job["id"], status="rendered")
    notify.send(
        f"Hazir: job {job['id']} ({channel['key']})\n{data['title']}\n{duration/60:.1f} dk\n"
        f"Onay icin: python -m pipeline.run_daily upload --job {job['id']}",
        photo=thumb,
    )
    return data


def do_upload(job_id: str, channels: dict) -> str:
    rows = {r["id"]: r for r in read_queue()}
    job = rows.get(job_id)
    if not job:
        raise SystemExit(f"Job bulunamadi: {job_id}")
    if job["status"] == "uploaded":
        raise SystemExit(f"Job {job_id} zaten yuklendi: {job['video_id']}")
    channel = channels[job["channel"]]
    jd = job_dir(job_id)
    data = json.loads((jd / "script.json").read_text(encoding="utf-8"))
    video_id = upload.upload_video(channel, jd / "video.mp4", jd / "thumbnail.jpg", data)
    update_queue_row(job_id, status="uploaded", video_id=video_id)
    msg = f"Yuklendi ve zamanlandi: https://youtu.be/{video_id} ({channel['key']})"
    print(msg)
    notify.send(msg)
    return video_id


def run_channel(channel_key: str, channels: dict, auto: bool) -> None:
    channel = channels[channel_key]
    job = pick_job(channel_key)
    if not job:
        print(f"[{channel_key}] kuyrukta bekleyen is yok")
        return
    try:
        render(job, channel)
        if auto:
            do_upload(job["id"], channels)
    except Exception as exc:  # noqa: BLE001
        traceback.print_exc()
        update_queue_row(job["id"], status="failed", notes=str(exc)[:200])
        notify.send(f"HATA job {job['id']} ({channel_key}): {exc}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=["render", "upload", "auto"])
    parser.add_argument("--channel")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--job")
    args = parser.parse_args(argv)
    _, channels = load_channels()

    if args.mode == "upload":
        if not args.job:
            parser.error("--job gerekli")
        do_upload(args.job, channels)
        return

    keys = list(channels) if args.all else [args.channel]
    if not keys or keys == [None]:
        parser.error("--channel <anahtar> veya --all gerekli")
    for key in keys:
        run_channel(key, channels, auto=(args.mode == "auto"))


if __name__ == "__main__":
    main(sys.argv[1:])
