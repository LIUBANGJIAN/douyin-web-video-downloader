FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先复制 requirements.txt 以利用缓存
COPY requirements.txt .

# 安装依赖并输出详细日志
RUN echo "=== 安装依赖 ===" && \
    pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt -v && \
    echo "=== 依赖安装完成 ===" && \
    pip list

# 复制应用代码
COPY app.py index.html ./
RUN mkdir -p /app/downloads

ENV DOWNLOAD_DIR=/app/downloads \
    PORT=8787

EXPOSE 8787
VOLUME ["/app/downloads"]

CMD ["python", "app.py"]