"""Audio transcription with word-level timestamps."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from faster_whisper import WhisperModel


@dataclass
class WordStamp:
    word: str
    start: float
    end: float


@dataclass
class TranscriptResult:
    words: list[WordStamp]
    full_text: str
    duration_seconds: float
    language: str | None


def format_timestamp(seconds: float) -> str:
    """Format seconds as HH:MM:SS.mmm or MM:SS.mmm."""
    if seconds < 0:
        seconds = 0.0
    total_ms = int(round(seconds * 1000))
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{ms:03d}"
    return f"{minutes:02d}:{secs:02d}.{ms:03d}"


def format_duration(seconds: float) -> str:
    """Human-readable call/recording duration."""
    if seconds < 0:
        seconds = 0.0
    total = int(round(seconds))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    parts: list[str] = []
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes or hours:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    parts.append(f"{secs} second{'s' if secs != 1 else ''}")
    return ", ".join(parts)


_model: WhisperModel | None = None
_model_key: tuple[str, str] | None = None


def get_model(model_size: str = "base", device: str = "cpu") -> WhisperModel:
    """Load and cache the Whisper model (downloads on first use if needed)."""
    global _model, _model_key
    compute_type = "int8" if device == "cpu" else "float16"
    key = (model_size, device)
    if _model is None or _model_key != key:
        _model = WhisperModel(model_size, device=device, compute_type=compute_type)
        _model_key = key
    return _model


def download_model(model_size: str = "base", device: str = "cpu") -> str:
    """Download (if needed) and load the selected Whisper model. Returns a status message."""
    get_model(model_size=model_size, device=device)
    return f"Model '{model_size}' is ready."


def transcribe_audio(
    audio_path: str | Path,
    model_size: str = "base",
    device: str = "cpu",
    language: str | None = None,
) -> TranscriptResult:
    """Transcribe an audio file with word-level timestamps."""
    path = Path(audio_path)
    if not path.is_file():
        raise FileNotFoundError(f"Audio file not found: {path}")

    model = get_model(model_size=model_size, device=device)
    segments, info = model.transcribe(
        str(path),
        word_timestamps=True,
        language=language,
        vad_filter=True,
    )

    words: list[WordStamp] = []
    text_parts: list[str] = []
    last_end = 0.0

    for segment in segments:
        if segment.text:
            text_parts.append(segment.text.strip())
        if segment.end is not None:
            last_end = max(last_end, float(segment.end))
        if not segment.words:
            continue
        for w in segment.words:
            token = (w.word or "").strip()
            if not token:
                continue
            words.append(
                WordStamp(
                    word=token,
                    start=float(w.start or 0.0),
                    end=float(w.end or w.start or 0.0),
                )
            )

    duration = float(info.duration) if info.duration else last_end
    return TranscriptResult(
        words=words,
        full_text=" ".join(text_parts).strip(),
        duration_seconds=duration,
        language=info.language,
    )
