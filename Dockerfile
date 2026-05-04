FROM python:3.11-slim

# Install ffmpeg, curl, nodejs (for PO token generation)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    nodejs \
    npm \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install yt-dlp with extras and PO token plugin
RUN pip install --no-cache-dir "yt-dlp[default]" && \
    pip install --no-cache-dir "yt-dlp-get-pot>=0.2.0" 2>/dev/null || true

COPY app.py .

EXPOSE 8080

CMD ["python", "app.py"]
