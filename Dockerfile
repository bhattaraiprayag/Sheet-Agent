FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-editable

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-editable

# ---------------------------------------------------------------------------
FROM python:3.12-slim

RUN groupadd -r sheetagent && useradd -r -g sheetagent sheetagent && \
    mkdir -p /app/sandbox && chown -R sheetagent:sheetagent /app/sandbox

WORKDIR /app

COPY --from=builder --chown=sheetagent:sheetagent /app /app

RUN chown -R sheetagent:sheetagent /app

USER sheetagent

EXPOSE 8000

ENV PATH="/app/.venv/bin:$PATH"

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"]

CMD ["uvicorn", "app.app:create_app", "--host", "0.0.0.0", "--port", "8000", "--factory"]
