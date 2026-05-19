FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -r requirements.txt

COPY app.py index.html ./
RUN mkdir -p /app/downloads

ENV DOWNLOAD_DIR=/app/downloads \
    PORT=8787

EXPOSE 8787
VOLUME ["/app/downloads"]
CMD ["python", "app.py"]
