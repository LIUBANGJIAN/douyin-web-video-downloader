FROM golang:1.21-alpine AS builder

WORKDIR /app

COPY main.go .

RUN go build -o web-video-downloader .

FROM alpine:latest

WORKDIR /app

RUN apk add --no-cache python3 py3-pip ffmpeg && \
    pip install --no-cache-dir yt-dlp

COPY --from=builder /app/web-video-downloader .
COPY index.html .

RUN mkdir -p downloads

EXPOSE 8080

CMD ["./web-video-downloader"]