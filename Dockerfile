FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ffmpeg curl supervisor \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libasound2 libpango-1.0-0 libcairo2 \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 --branch main \
    https://github.com/Evil0ctal/Douyin_TikTok_Download_API.git /douyin-api

WORKDIR /douyin-api
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install chromium

COPY app.py cookie_manager.py douyin_client.py index.html ./
COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && mkdir -p /data/douyin /app/downloads

ENV DOUYIN_API_URL=http://127.0.0.1:80 \
    DOUYIN_CONFIG_PATH=/data/douyin/config.yaml \
    DOWNLOAD_DIR=/app/downloads \
    PORT=8787 \
    COOKIE_CHECK_INTERVAL=300

EXPOSE 8787

VOLUME ["/data/douyin", "/app/downloads"]

ENTRYPOINT ["/entrypoint.sh"]
