FROM python:3.12-alpine

RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    libffi-dev \
    openssl-dev \
    && rm -rf /var/cache/apk/*

WORKDIR /app

RUN mkdir -p logs

RUN python -m venv /app/venv

# Enable venv
ENV PATH="/app/venv/bin:$PATH"

COPY . .

ENV PATH="/app/venv/bin:$PATH"

RUN pip install -r requirements.txt


CMD  ["python", "./main.py"]

# Healthcheck
HEALTHCHECK --interval=15s --timeout=5s CMD ps aux | grep '[p]ython' || exit 1