FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

COPY ./google_service/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./google_service/app /app
COPY ./utils /app/utils

CMD ["python", "main.py"]