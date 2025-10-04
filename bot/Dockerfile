# worker-manager/Dockerfile
ARG PYTHON_VERSION=3.12.3

# ─── builder ────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# gcc уже был, добавляем недостающее:
#   • build-essential → libc6-dev, make, g++
#   • pkg-config      → .pc-файлы для cairo
#   • libcairo2-dev   → headers + либы
#   • libgirepository1.0-dev → иногда требует gir для cairo
RUN apt-get update && apt-get install --no-install-recommends -y \
        build-essential \
        pkg-config \
        libcairo2-dev \
        libgirepository1.0-dev \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1) deps + shared
COPY bot/requirements.txt .
COPY shared/ ./shared

RUN pip install --upgrade pip \
 && pip install --prefix=/install -r requirements.txt \
 && pip install --prefix=/install ./shared

# ─── runtime ────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    TZ=Europe/Moscow

# только то, что нужно в production
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        tzdata \
        libcairo2 \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# bring in installed packages
COPY --from=builder /install /usr/local

# copy your service code
COPY bot/ .

# ensure pyrlottie bundled binaries are executable
RUN /bin/sh -lc 'chmod +x /usr/local/lib/python*/site-packages/pyrlottie/linux_*/* 2>/dev/null || true'

ENTRYPOINT ["python3", "main.py"]
