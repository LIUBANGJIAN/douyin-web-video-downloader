FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY index.html .

RUN mkdir -p downloads

EXPOSE 8080

CMD ["python", "app.py"]