# ------------------------------------------
# Stage 1: Build dependencies and install Python packages
# ------------------------------------------
ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends -y gcc libpq-dev wget && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# ------------------------------------------
# Stage 2: Final runtime image
# ------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

#ENTRYPOINT ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8080"]
