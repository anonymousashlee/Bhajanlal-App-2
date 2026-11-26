# Bhajanlal Python API (serve/backend.py, aiohttp) — multi-stage, non-root.
FROM python:3.12-slim AS builder
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements-api.txt .
RUN pip install -r requirements-api.txt

FROM python:3.12-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:/usr/local/bin:$PATH" \
    BHAJANLAL_BACKEND_HOST=0.0.0.0 \
    BHAJANLAL_BACKEND_PORT=8790 \
    BHAJANLAL_OPENCODE_CWD=/app
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --uid 10001 appuser
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
# Install opencode CLI (Linux x64)
RUN curl -fsSL https://github.com/anomalyco/opencode/releases/latest/download/opencode-linux-x64.tar.gz -o /tmp/opencode.tar.gz && \
    tar -xzf /tmp/opencode.tar.gz -C /usr/local/bin && \
    rm /tmp/opencode.tar.gz && \
    chmod +x /usr/local/bin/opencode
# Create minimal opencode config for free model access
RUN mkdir -p /home/appuser/.config/opencode && \
    echo '{"$schema":"https://opencode.ai/config.json","model":"opencode/beam-free"}' > /home/appuser/.config/opencode/opencode.json
COPY serve/ ./serve/
USER appuser
ENV HOME=/home/appuser
ENV PATH="/opt/venv/bin:/usr/local/bin:$PATH"
EXPOSE 8790
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8790/health', timeout=4).status==200 else 1)"
CMD ["python", "serve/backend.py"]
