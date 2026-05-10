FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    nmap \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p reports

EXPOSE 5000

CMD ["python", "app.py"]