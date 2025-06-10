ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update \
 && apt-get install --no-install-recommends -y gcc libpq-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY watcher/requirements.txt .

RUN pip install --upgrade pip \
 && pip install --prefix=/install -r requirements.txt

# 1) copy & install service deps + shared
COPY shared/ ./shared
RUN pip install --prefix=/install ./shared

# ─── runtime ────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# bring in installed packages
COPY --from=builder /install /usr/local

# copy your service code
COPY watcher/ .

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
