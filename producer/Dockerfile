FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt tenacity circuitbreaker

RUN apt-get update && apt-get install -y netcat-openbsd

COPY . .

CMD echo "Starting producer..." && python -u main.py