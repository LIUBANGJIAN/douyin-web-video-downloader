FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt -v && \
    # 找到 douyin-downloader 的 run.py 位置并建立软链接
    find /usr/local/lib -name "run.py" -path "*douyin*" | head -1 | xargs -I {} ln -s {} /app/douyin_run.py || true

# 复制应用代码
COPY app.py index.html ./
RUN mkdir -p /app/downloads

ENV DOWNLOAD_DIR=/app/downloads \
    PORT=8787

EXPOSE 8787
VOLUME ["/app/downloads"]

CMD ["python", "app.py"]