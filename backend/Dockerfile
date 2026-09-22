FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DATA_DIR=/app/data

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Run as a non-root user. uid 1000 matches the default desktop user on most
# Linux hosts so the bind-mounted ./data directory stays writable.
RUN useradd --uid 1000 --create-home appuser && chown appuser:appuser /app
USER appuser

# Pre-download the local embedding model (~80 MB) at build time so the
# container starts instantly and never needs internet for RAG.
RUN python -c "from chromadb.utils.embedding_functions import DefaultEmbeddingFunction as F; F()(['warm-up'])"

COPY --chown=appuser:appuser app ./app

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=20s --retries=6 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/api/v1/health', timeout=3).status == 200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
