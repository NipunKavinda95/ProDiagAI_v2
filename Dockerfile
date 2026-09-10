FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install backend dependencies first for better Docker layer caching
COPY backend/requirements.txt /app/backend/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r /app/backend/requirements.txt

# Copy backend application
COPY backend /app/backend

# Copy ML model artifacts
COPY ml /app/ml

# Copy RAG knowledge base
COPY knowledge-base /app/knowledge-base

# Copy simulator for later Render Background Worker deployment
COPY simulator /app/simulator

# Render provides PORT automatically.
# 10000 is the default fallback for local Docker testing.
ENV PORT=10000

EXPOSE 10000

# Run Flask through Gunicorn.
# --chdir is important because the backend uses imports such as:
# from services...
CMD ["sh", "-c", "gunicorn --chdir /app/backend --bind 0.0.0.0:${PORT:-10000} --workers 1 --threads 4 --timeout 120 app:app"]