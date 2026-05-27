FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

COPY ./azure_service/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./azure_service/app /app
COPY ./utils /app/utils

CMD ["python", "main.py"]