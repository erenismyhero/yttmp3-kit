# YT → MP3

A local web app to convert any YouTube link to a downloadable MP3.

## Requirements

- Python 3.8+
- ffmpeg installed on your system

## Setup

```bash
pip install -r requirements.txt
```

**Install ffmpeg** (if not already installed):
- **macOS**: `brew install ffmpeg`
- **Ubuntu/Debian**: `sudo apt install ffmpeg`
- **Windows**: Download from https://ffmpeg.org/download.html and add to PATH

## Run

```bash
python app.py
```

Then open **http://localhost:5000** in your browser.

## Usage

1. Paste a YouTube URL into the input field
2. Click **Convert**
3. Wait for the download button to appear
4. Click **Download MP3**

## Notes

- Audio quality: 192kbps MP3
- Files are stored temporarily in `/tmp/yt2mp3/`
- Works with any yt-dlp supported URL (YouTube, etc.)
