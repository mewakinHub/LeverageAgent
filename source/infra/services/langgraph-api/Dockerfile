FROM python:3.11-slim

# yt-dlp + ffmpeg for audio/subtitles work + browser deps for impersonation
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg ca-certificates curl wget \
    # Browser dependencies for yt-dlp impersonation
    chromium chromium-driver \
 && rm -rf /var/lib/apt/lists/*

# yt-dlp + recommended extras (fixes impersonation warning on YouTube)
RUN pip install --no-cache-dir yt-dlp[default]

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
