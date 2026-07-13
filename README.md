# Audio Transcript → Word

Desktop app that turns call/audio recordings into a Microsoft Word transcript with:

- **Call recording time** (human-readable duration + timestamp)
- **Word-by-word transcript** with start/end timestamps
- **Full transcript** text
- Browse window to select **one or many** audio files

## Supported audio

`.wav`, `.mp3`, `.m4a`, `.mp4`, `.flac`, `.ogg`, `.wma`, `.aac`, `.webm`, and related formats (via faster-whisper / ffmpeg).

## Run from source

```powershell
cd audio-transcript
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

First transcription downloads the selected Whisper model (default: `base`).

## Build the Windows .exe

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
.\build_exe.bat
```

The executable is written to `dist\AudioTranscript.exe`.

> Note: the `.exe` does **not** bundle speech models. On first use it downloads the model (needs internet once). Keep the app online for that first run.

## Usage

1. Click **Browse files…** and select one or more recordings
2. Choose an **output folder**
3. Pick a Whisper model (`base` is a good default)
4. Click **Generate Word transcripts**
5. Open the generated `*_transcript.docx` files in Microsoft Word

## Project layout

| File | Purpose |
|------|---------|
| `main.py` | GUI (browse, queue, progress) |
| `transcriber.py` | Word-level transcription |
| `word_export.py` | Word `.docx` export |
| `build_exe.bat` | PyInstaller build |
| `requirements.txt` | Python dependencies |
