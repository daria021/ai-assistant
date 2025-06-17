ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update \
 && apt-get install --no-install-recommends -y gcc libpq-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY posts-service/requirements.txt .

RUN pip install --upgrade pip \
 && pip install --prefix=/install -r requirements.txt

# 1) copy & install service deps + shared
COPY shared/ ./shared
RUN pip install --prefix=/install ./shared

# ─── runtime ────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# Set the TZ environment variable
ENV TZ=Europe/Moscow

# Install tzdata, configure the timezone, and clean up
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata \
 && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
 && echo $TZ > /etc/timezone \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# bring in installed packages
COPY --from=builder /install /usr/local

# copy your service code
COPY posts-service/ .

ENTRYPOINT ["python3", "main.py"]
