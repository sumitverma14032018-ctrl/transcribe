# TubeScribe

Local YouTube and audio transcription using OpenAI Whisper (`large-v3`). You can run a small web UI or use the command-line scripts.

Audio from YouTube is downloaded as MP3 into `downloads/`. Transcripts are written incrementally to `transcriptions/`.

## Requirements

- Python 3.9+
- [FFmpeg](https://ffmpeg.org/) (needed to extract MP3 from YouTube)
- A machine that can load Whisper `large-v3` (GPU recommended; CPU works but is slow)

Install Python dependencies (from a virtualenv):

```bash
pip install fastapi uvicorn openai-whisper yt-dlp
```

## Web UI

From the project root:

```bash
python api.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Paste a YouTube URL or an absolute path to a local audio file, then transcribe. Progress and logs stream in the page; finished text is saved under `transcriptions/`.

## Command line

YouTube URL or local file, then transcribe:

```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"
python main.py /path/to/audio.mp3
```

Download audio only:

```bash
python youtube_to_mp3.py "https://www.youtube.com/watch?v=VIDEO_ID"
python extractor.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

Transcribe an existing MP3:

```bash
python transcribe_mp3.py input.mp3 transcriptions/output.txt
python transcribe_mp3.py input.mp3 transcriptions/output.txt --model large-v3
```

## Layout

| Path | Role |
|------|------|
| `api.py` | FastAPI app, SSE status, static UI |
| `ui/` | TubeScribe front end |
| `extractor.py` / `youtube_to_mp3.py` | YouTube → MP3 via yt-dlp |
| `transcriber.py` / `transcribe_mp3.py` | Whisper transcription |
| `main.py` | Combined extract + transcribe CLI |

`downloads/` and `transcriptions/` are generated at runtime and are not committed.
