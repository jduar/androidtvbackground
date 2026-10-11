FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt flask==3.0.3

COPY . .

EXPOSE 5000

CMD ["python", "server.py"]
