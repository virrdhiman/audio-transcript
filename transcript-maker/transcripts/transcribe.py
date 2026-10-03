from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


AUDIO_EXTENSIONS = {
    ".flac",
    ".m4a",
    ".mp3",
    ".mp4a",
    ".oga",
    ".ogg",
    ".opus",
    ".wav",
    ".webm",
}

VIDEO_EXTENSIONS = {
    ".avi",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpeg",
    ".mpg",
    ".webm",
    ".wmv",
}


def require_openai_client() -> Any:
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError(
            "Missing dependency: openai\n"
            "Install it with: python -m pip install -r requirements.txt"
        )

    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "Missing OPENAI_API_KEY environment variable.\n"
            "PowerShell example: $env:OPENAI_API_KEY='your_api_key_here'"
        )

    return OpenAI()


def extract_audio(video_path: Path, work_dir: Path) -> Path:
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise RuntimeError(
            "This looks like a video file, but ffmpeg is not installed or not on PATH.\n"
            "Install ffmpeg, then run the command again."
        )

    audio_path = work_dir / f"{video_path.stem}.mp3"
    command = [
        ffmpeg_path,
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-acodec",
        "libmp3lame",
        "-ar",
        "44100",
        "-ac",
        "2",
        str(audio_path),
    ]
    subprocess.run(command, check=True)
    return audio_path


def choose_input_file(input_path: Path, work_dir: Path) -> Path:
    suffix = input_path.suffix.lower()
    if suffix in AUDIO_EXTENSIONS:
        return input_path
    if suffix in VIDEO_EXTENSIONS:
        return extract_audio(input_path, work_dir)

    raise RuntimeError(f"Unsupported file type: {input_path.suffix}")


def format_timestamp(seconds: float) -> str:
    milliseconds = int(round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def write_srt(segments: list[dict[str, Any]], output_path: Path) -> None:
    lines: list[str] = []
    for index, segment in enumerate(segments, start=1):
        start = format_timestamp(float(segment["start"]))
        end = format_timestamp(float(segment["end"]))
        text = str(segment["text"]).strip()
        lines.extend([str(index), f"{start} --> {end}", text, ""])

    output_path.write_text("\n".join(lines), encoding="utf-8")


def transcribe(input_file: Path, output_dir: Path, model: str, language: str | None) -> None:
    client = require_openai_client()
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        audio_file = choose_input_file(input_file, Path(temp_dir))
        with audio_file.open("rb") as media:
            request: dict[str, Any] = {
                "model": model,
                "file": media,
                "response_format": "verbose_json",
            }
            if language:
                request["language"] = language

            result = client.audio.transcriptions.create(**request)

    data = result.model_dump() if hasattr(result, "model_dump") else dict(result)
    base_name = input_file.stem

    text = str(data.get("text", "")).strip()
    (output_dir / f"{base_name}.txt").write_text(text + "\n", encoding="utf-8")
    (output_dir / f"{base_name}.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    segments = data.get("segments") or []
    if segments:
        write_srt(segments, output_dir / f"{base_name}.srt")

    print(f"Transcript written to: {output_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create transcripts from audio or video files."
    )
    parser.add_argument("input", help="Path to an audio or video file")
    parser.add_argument(
        "-o",
        "--output-dir",
        default="transcripts",
        help="Folder where transcript files are saved",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-transcribe",
        help="OpenAI transcription model to use",
    )
    parser.add_argument(
        "--language",
        help="Optional language code, such as en or hi",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_file = Path(args.input).expanduser().resolve()
    if not input_file.exists():
        print(f"File not found: {input_file}", file=sys.stderr)
        raise SystemExit(1)

    try:
        transcribe(
            input_file=input_file,
            output_dir=Path(args.output_dir).expanduser().resolve(),
            model=args.model,
            language=args.language,
        )
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc


def run_gui() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, simpledialog

    root = tk.Tk()
    root.withdraw()

    input_name = filedialog.askopenfilename(
        title="Choose audio or video file",
        filetypes=[
            ("Audio and video files", "*.mp3 *.wav *.m4a *.flac *.ogg *.opus *.mp4 *.mov *.mkv *.avi *.webm *.wmv"),
            ("All files", "*.*"),
        ],
    )
    if not input_name:
        return

    input_file = Path(input_name).resolve()
    output_name = filedialog.askdirectory(
        title="Choose folder to save transcript",
        initialdir=str(input_file.parent),
    )
    if not output_name:
        return

    if not os.environ.get("OPENAI_API_KEY"):
        api_key = simpledialog.askstring(
            "OpenAI API Key",
            "Enter your OpenAI API key:",
            show="*",
        )
        if not api_key:
            messagebox.showerror("Transcript Maker", "OpenAI API key is required.")
            return
        os.environ["OPENAI_API_KEY"] = api_key

    try:
        transcribe(
            input_file=input_file,
            output_dir=Path(output_name).resolve(),
            model="gpt-4o-transcribe",
            language=None,
        )
    except Exception as exc:
        messagebox.showerror("Transcript Maker", str(exc))
        return

    messagebox.showinfo(
        "Transcript Maker",
        f"Transcript created successfully.\n\nSaved in:\n{output_name}",
    )


if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_gui()
    else:
        main()
