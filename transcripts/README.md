# Transcript Maker

Create text transcripts from audio files, and from video files when `ffmpeg` is installed.

## Setup

Install the Python dependency:

```powershell
cd "C:\Users\virrd\OneDrive\Desktop\Programs\Transcript_Maker"
python -m pip install -r requirements.txt
```

Set your OpenAI API key:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

For video files, install `ffmpeg` and make sure it is available on PATH.

## Usage

Double-click the Windows app:

```powershell
C:\Users\virrd\OneDrive\Desktop\Programs\Transcript_Maker\transcripts\dist\TranscriptMaker.exe
```

It will ask you to choose the audio or video file, then ask where to save the transcript. If `OPENAI_API_KEY` is not already set, it will ask for your API key.

Audio:

```powershell
python transcribe.py "C:\path\to\audio.mp3"
```

Video:

```powershell
python transcribe.py "C:\path\to\video.mp4"
```

Choose an output folder:

```powershell
python transcribe.py "C:\path\to\meeting.mp3" -o "C:\Users\virrd\OneDrive\Desktop\Programs\Transcript_Maker\output"
```

Specify a language:

```powershell
python transcribe.py "C:\path\to\audio.mp3" --language en
```

The program writes:

- `.txt` for the plain transcript
- `.json` for the full model response
- `.srt` subtitles when timestamp segments are returned
