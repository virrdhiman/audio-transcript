# Transcript Maker

Audio and video transcription using the OpenAI API. Source code lives in the `transcripts/` folder.

## Quick start

```powershell
cd "C:\Users\virrd\OneDrive\Desktop\Programs\Transcript_Maker\transcripts"
python -m pip install -r requirements.txt
$env:OPENAI_API_KEY="your_api_key_here"
python transcribe.py "C:\path\to\audio.mp3"
```

See [transcripts/README.md](transcripts/README.md) for full setup, usage, and EXE build instructions.
