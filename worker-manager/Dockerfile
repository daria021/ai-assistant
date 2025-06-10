# worker-manager/Dockerfile
ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update \
 && apt-get install --no-install-recommends -y gcc libpq-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1) copy & install service deps + shared
COPY worker-manager/requirements.txt .

RUN pip install --upgrade pip \
 && pip install --prefix=/install -r requirements.txt

COPY shared/ ./shared

RUN pip install --prefix=/install ./shared

# ─── runtime ────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# bring in installed packages
COPY --from=builder /install /usr/local

# copy your service code
COPY worker-manager/ .

COPY .env ./.env

ENTRYPOINT ["python3", "main.py"]
