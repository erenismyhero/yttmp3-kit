import os
import uuid
import threading
from flask import Flask, request, jsonify, send_file, render_template_string
import yt_dlp

app = Flask(__name__)
DOWNLOAD_DIR = os.path.join("/tmp", "yt2mp3")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

jobs = {}

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Eren's YTTMP3 Kit</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #a8d8ea;
    --surface: rgba(255,255,255,0.55);
    --border: rgba(100,180,220,0.45);
    --accent: #1a7fb5;
    --accent2: #5bc8f5;
    --text: #0d3d57;
    --muted: #4a8faa;
    --success: #1db98a;
  }

  @keyframes blobMove1 {
    0%,100% { transform: translate(0,0) scale(1); }
    33%      { transform: translate(40px,-30px) scale(1.05); }
    66%      { transform: translate(-20px,20px) scale(0.97); }
  }
  @keyframes blobMove2 {
    0%,100% { transform: translate(0,0) scale(1); }
    33%     { transform: translate(-50px,25px) scale(1.08); }
    66%     { transform: translate(30px,-15px) scale(0.95); }
  }
  @keyframes blobMove3 {
    0%,100% { transform: translate(0,0) scale(1); }
    50%     { transform: translate(20px,40px) scale(1.06); }
  }
  @keyframes slide {
    0%   { transform: translateX(-200%); }
    100% { transform: translateX(350%); }
  }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'DM Mono', monospace;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    overflow-x: hidden;
    position: relative;
  }

  .blob {
    position: fixed;
    border-radius: 50%;
    filter: blur(70px);
    opacity: 0.6;
    pointer-events: none;
    z-index: 0;
  }
  .blob1 { width:520px;height:520px;background:#7ec8e3;top:-120px;left:-120px;animation:blobMove1 9s ease-in-out infinite; }
  .blob2 { width:420px;height:420px;background:#b8e4f9;bottom:-90px;right:-90px;animation:blobMove2 11s ease-in-out infinite; }
  .blob3 { width:320px;height:320px;background:#d0f0ff;top:45%;left:58%;animation:blobMove3 8s ease-in-out infinite; }

  .container {
    width: 100%;
    max-width: 680px;
    position: relative;
    z-index: 1;
  }

  header { margin-bottom: 3rem; }

  .logo {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(2rem, 7vw, 4.2rem);
    letter-spacing: 0.04em;
    line-height: 1;
    color: var(--text);
  }
  .logo span { color: var(--accent); }

  .tagline {
    font-size: 0.7rem;
    color: var(--muted);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.5rem;
  }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 2rem;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(12px);
    border-radius: 4px;
    box-shadow: 0 8px 32px rgba(26,127,181,0.1);
  }

  .card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
  }

  .input-row {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
  }

  input[type="text"] {
    flex: 1;
    background: rgba(255,255,255,0.6);
    border: 1px solid var(--border);
    color: var(--text);
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    padding: 0.85rem 1rem;
    outline: none;
    transition: border-color 0.2s;
    border-radius: 2px;
  }
  input[type="text"]:focus { border-color: var(--accent); }
  input[type="text"]::placeholder { color: var(--muted); }

  button {
    background: var(--accent);
    border: none;
    color: white;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.1rem;
    letter-spacing: 0.1em;
    padding: 0.85rem 1.5rem;
    cursor: pointer;
    transition: background 0.2s, transform 0.1s;
    white-space: nowrap;
    border-radius: 2px;
  }
  button:hover { background: #1e93d4; }
  button:active { transform: scale(0.97); }
  button:disabled { background: var(--muted); cursor: not-allowed; transform: none; }

  .status-box {
    display: none;
    background: rgba(255,255,255,0.4);
    border: 1px solid var(--border);
    padding: 1.25rem;
    border-radius: 2px;
  }
  .status-box.visible { display: block; }

  .status-label {
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.5rem;
  }

  .status-text { font-size: 0.8rem; color: var(--text); }

  .progress-bar-wrap {
    height: 3px;
    background: var(--border);
    margin-top: 1rem;
    overflow: hidden;
    border-radius: 2px;
  }

  .progress-bar {
    height: 100%;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    width: 0%;
    transition: width 0.3s;
  }
  .progress-bar.indeterminate {
    width: 40%;
    animation: slide 1.2s ease-in-out infinite;
  }

  .download-btn {
    display: none;
    width: 100%;
    background: var(--success);
    color: #fff;
    margin-top: 1rem;
    font-size: 1rem;
    padding: 1rem;
    text-align: center;
    border-radius: 2px;
  }
  .download-btn.visible { display: block; }
  .download-btn:hover { background: #17a87a; }

  .error-text { color: #c0392b; }

  .info-grid {
    display: none;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }
  .info-grid.visible { display: grid; }

  .info-cell {
    background: rgba(255,255,255,0.4);
    border: 1px solid var(--border);
    padding: 0.75rem;
    border-radius: 2px;
  }
  .info-cell .label {
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.25rem;
  }
  .info-cell .value {
    font-size: 0.8rem;
    color: var(--text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  footer {
    margin-top: 2rem;
    font-size: 0.65rem;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-align: center;
  }
</style>
</head>
<body>
<div class="blob blob1"></div>
<div class="blob blob2"></div>
<div class="blob blob3"></div>

<div class="container">
  <header>
    <div class="logo">Eren's <span>YTTMP3</span> Kit</div>
    <div class="tagline">YouTube audio extractor</div>
  </header>

  <div class="card">
    <div class="input-row">
      <input type="text" id="urlInput" placeholder="https://youtube.com/watch?v=..." />
      <button id="convertBtn" onclick="startConvert()">Convert</button>
    </div>

    <div class="info-grid" id="infoGrid">
      <div class="info-cell">
        <div class="label">Title</div>
        <div class="value" id="infoTitle">—</div>
      </div>
      <div class="info-cell">
        <div class="label">Duration</div>
        <div class="value" id="infoDuration">—</div>
      </div>
    </div>

    <div class="status-box" id="statusBox">
      <div class="status-label">Status</div>
      <div class="status-text" id="statusText">Initializing...</div>
      <div class="progress-bar-wrap">
        <div class="progress-bar indeterminate" id="progressBar"></div>
      </div>
    </div>

    <button class="download-btn" id="downloadBtn">⬇ Download MP3</button>
  </div>

  <footer>powered by yt-dlp + ffmpeg &nbsp;·&nbsp; audio quality: 192kbps</footer>
</div>

<script>
let pollInterval = null;

function fmtDuration(sec) {
  if (!sec) return '—';
  const m = Math.floor(sec / 60), s = sec % 60;
  return m + ':' + String(s).padStart(2, '0');
}

async function startConvert() {
  const url = document.getElementById('urlInput').value.trim();
  if (!url) return;

  const btn = document.getElementById('convertBtn');
  const statusBox = document.getElementById('statusBox');
  const statusText = document.getElementById('statusText');
  const progressBar = document.getElementById('progressBar');
  const downloadBtn = document.getElementById('downloadBtn');
  const infoGrid = document.getElementById('infoGrid');

  btn.disabled = true;
  downloadBtn.classList.remove('visible');
  infoGrid.classList.remove('visible');
  statusBox.classList.add('visible');
  statusText.classList.remove('error-text');
  statusText.textContent = 'Fetching video info...';
  progressBar.className = 'progress-bar indeterminate';

  try {
    const res = await fetch('/convert', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({url})
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Failed');

    const jobId = data.job_id;
    if (data.title) {
      document.getElementById('infoTitle').textContent = data.title;
      document.getElementById('infoDuration').textContent = fmtDuration(data.duration);
      infoGrid.classList.add('visible');
    }

    pollInterval = setInterval(() => pollStatus(jobId), 1000);
  } catch(e) {
    statusText.textContent = e.message;
    statusText.classList.add('error-text');
    btn.disabled = false;
  }
}

async function pollStatus(jobId) {
  const statusText = document.getElementById('statusText');
  const progressBar = document.getElementById('progressBar');
  const downloadBtn = document.getElementById('downloadBtn');
  const btn = document.getElementById('convertBtn');

  const res = await fetch('/status/' + jobId);
  const data = await res.json();

  statusText.textContent = data.message || data.status;

  if (data.status === 'done') {
    clearInterval(pollInterval);
    progressBar.className = 'progress-bar';
    progressBar.style.width = '100%';
    downloadBtn.classList.add('visible');
    downloadBtn.onclick = () => { window.location = '/download/' + jobId; };
    btn.disabled = false;
  } else if (data.status === 'error') {
    clearInterval(pollInterval);
    statusText.classList.add('error-text');
    btn.disabled = false;
  }
}

document.getElementById('urlInput').addEventListener('keydown', e => {
  if (e.key === 'Enter') startConvert();
});
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/convert", methods=["POST"])
def convert():
    data = request.get_json()
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
        title = info.get("title", "Unknown")
        duration = info.get("duration", 0)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "queued", "message": "Queued...", "file": None}

    thread = threading.Thread(target=download_audio, args=(job_id, url), daemon=True)
    thread.start()

    return jsonify({"job_id": job_id, "title": title, "duration": duration})

def download_audio(job_id, url):
    out_path = os.path.join(DOWNLOAD_DIR, job_id)
    os.makedirs(out_path, exist_ok=True)

    def progress_hook(d):
        if d["status"] == "downloading":
            pct = d.get("_percent_str", "").strip()
            speed = d.get("_speed_str", "").strip()
            jobs[job_id]["message"] = f"Downloading... {pct} at {speed}"
        elif d["status"] == "finished":
            jobs[job_id]["message"] = "Converting to MP3..."

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(out_path, "%(title)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "progress_hooks": [progress_hook],
        "quiet": True,
    }

    try:
        jobs[job_id]["status"] = "downloading"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        mp3_files = [f for f in os.listdir(out_path) if f.endswith(".mp3")]
        if not mp3_files:
            raise Exception("MP3 file not found after conversion")

        jobs[job_id]["status"] = "done"
        jobs[job_id]["message"] = "Ready to download!"
        jobs[job_id]["file"] = os.path.join(out_path, mp3_files[0])
        jobs[job_id]["filename"] = mp3_files[0]
    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["message"] = str(e)

@app.route("/status/<job_id>")
def status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"status": "error", "message": "Job not found"}), 404
    return jsonify(job)

@app.route("/download/<job_id>")
def download(job_id):
    job = jobs.get(job_id)
    if not job or job["status"] != "done":
        return "Not ready", 404
    return send_file(job["file"], as_attachment=True, download_name=job["filename"])

if __name__ == "__main__":
    import threading
    port = int(os.environ.get("PORT", 8080))
    print(f"Eren's YTTMP3 Kit running at http://localhost:{port}")
    
    app.run(debug=False, port=port, host="0.0.0.0")
