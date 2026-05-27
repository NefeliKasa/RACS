FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

COPY ./racs_controller/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./racs_controller /app
COPY ./k8s_utils /app/k8s_utils
COPY ./utils /app/utils

CMD ["python", "-u", "main.py"]