"""Adim 4: FFmpeg ile Ken Burns efektli slayt + ses + alcak muzik."""
from __future__ import annotations

import subprocess
from pathlib import Path


def _scene_durations(scenes: list[dict], total: float) -> list[float]:
    weights = [max(1, len(s["narration"].split())) for s in scenes]
    wsum = sum(weights)
    return [total * w / wsum for w in weights]


def _render_clip(image: Path, seconds: float, out: Path, w: int, h: int, fps: int, idx: int) -> None:
    frames = max(int(seconds * fps), fps)
    # Tek sayili sahnelerde yakinlas, cift sayili sahnelerde uzaklas.
    if idx % 2 == 0:
        zoom = "min(zoom+0.0008,1.18)"
    else:
        zoom = "if(eq(on,1),1.18,max(zoom-0.0008,1.0))"
    vf = (
        f"scale={w*2}:{h*2}:force_original_aspect_ratio=increase,crop={w*2}:{h*2},"
        f"zoompan=z='{zoom}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={w}x{h}:fps={fps},"
        f"format=yuv420p"
    )
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(image),
        "-vf", vf, "-t", f"{seconds:.3f}", "-r", str(fps),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-an", str(out),
    ]
    subprocess.run(cmd, check=True)


def build_video(scenes: list[dict], images: list[Path], audio: Path, duration: float,
                channel: dict, workdir: Path, out: Path) -> Path:
    w, h, fps = int(channel["width"]), int(channel["height"]), int(channel["fps"])
    clips_dir = workdir / "clips"
    clips_dir.mkdir(exist_ok=True)
    durations = _scene_durations(scenes, duration + 1.0)

    clip_paths = []
    for i, (img, secs) in enumerate(zip(images, durations)):
        clip = clips_dir / f"clip_{i:03d}.mp4"
        if not clip.exists():
            _render_clip(img, secs, clip, w, h, fps, i)
        clip_paths.append(clip)

    concat_list = workdir / "concat.txt"
    concat_list.write_text("".join(f"file '{p.resolve()}'\n" for p in clip_paths))
    silent = workdir / "silent.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(concat_list), "-c", "copy", str(silent)], check=True)

    music = Path(__file__).resolve().parent.parent / channel.get("music", "")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(audio)]
    if music.is_file():
        vol = float(channel["music_volume"])
        cmd += ["-stream_loop", "-1", "-i", str(music),
                "-filter_complex",
                f"[2:a]volume={vol}[m];[1:a][m]amix=inputs=2:duration=first:dropout_transition=3[a]",
                "-map", "0:v", "-map", "[a]"]
    else:
        cmd += ["-map", "0:v", "-map", "1:a"]
    cmd += ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)]
    subprocess.run(cmd, check=True)
    return out
