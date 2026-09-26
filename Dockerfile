# syntax=docker/dockerfile:1
# =============================================================================
# Stage 1: builder -- installs dependencies into a venv and nothing else.
# No compiler installed here: azure-search-documents and langchain-openai
# both install from prebuilt wheels on standard platforms.
# =============================================================================
FROM python:3.12-slim AS builder

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 2: runtime -- just the venv and application source.
# =============================================================================
FROM python:3.12-slim AS runtime

RUN groupadd --system app && useradd --system --gid app --no-create-home app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

WORKDIR /app
COPY domain/ ./domain/
COPY infrastructure/ ./infrastructure/
COPY server.py settings.py ./

RUN chown -R app:app /app
USER app

EXPOSE 8899

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import socket; s = socket.socket(); s.settimeout(3); s.connect(('127.0.0.1', 8899)); s.close()" || exit 1

CMD ["python", "server.py"]