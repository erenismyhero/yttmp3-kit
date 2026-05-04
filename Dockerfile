FROM python:3.11-slim

# Install ffmpeg and deno (JS runtime for yt-dlp)
RUN apt-get update && apt-get install -y ffmpeg curl unzip && \
    curl -fsSL https://deno.land/install.sh | sh && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV DENO_INSTALL="/root/.deno"
ENV PATH="$DENO_INSTALL/bin:$PATH"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8080

CMD ["python", "app.py"]
