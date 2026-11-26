# Bhajanlal Python API (serve/backend.py, aiohttp) — multi-stage, non-root.
#
# Exact local commands:
#   docker build -t bhajanlal-api:local .
#   docker run --rm -p 8790:8790 -e BHAJANLAL_BACKEND_HOST=0.0.0.0 bhajanlal-api:local
#   curl -fsS http://127.0.0.1:8790/health          # smoke test
#   python3 evals/harness.py --self-check           # offline test suite

# ---- Stage 1: builder — install pinned deps into a venv ----
FROM python:3.12-slim AS builder
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements-api.txt .
RUN pip install -r requirements-api.txt

# ---- Stage 2: runtime — slim image, no compilers, non-root ----
FROM python:3.12-slim AS runtime
# BHAJANLAL_BACKEND_HOST must be 0.0.0.0 — the app default 127.0.0.1 is unreachable
# from outside the container.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    BHAJANLAL_BACKEND_HOST=0.0.0.0 \
    BHAJANLAL_BACKEND_PORT=8790
RUN useradd --create-home --uid 10001 appuser
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY serve/ ./serve/
USER appuser
EXPOSE 8790
# Container health = real /health endpoint, so orchestrators gate on liveness
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8790/health', timeout=4).status==200 else 1)"
CMD ["python", "serve/backend.py"]