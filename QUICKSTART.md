# Quick Start

This guide covers prerequisites, installation, and running SheetAgent locally or via Docker.

## Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| **Python 3.12+** | Runtime | [python.org](https://www.python.org/downloads/) |
| **uv** | Package & project manager | [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) |
| **Docker** *(optional)* | Containerised execution | [docker.com](https://docs.docker.com/get-docker/) |

## Local Development

### 1. Clone and Install

```bash
git clone <repository-url>
cd Sheet-Agent
uv sync
```

`uv sync` creates a `.venv` directory and installs all dependencies locked in `uv.lock`.

### 2. Environment Configuration

```bash
# Linux / macOS
cp .env.example .env

# Windows PowerShell
Copy-Item .env.example .env
```

Edit `.env` and set at minimum:

- `OPENAI_API_KEY` — required for semantic column mapping.

### 3. Run the Server

```bash
uv run uvicorn app.app:create_app --host 0.0.0.0 --port 8000 --factory
```

The API is available at `http://localhost:8000`. Interactive documentation is served at `http://localhost:8000/docs`.

### 4. Run Tests

```bash
uv run pytest
```

### 5. Run Linting

```bash
uv run ruff check .
uv run ruff format --check .
```

## Docker Setup

### Build and Run

```bash
docker compose up --build
```

The API is exposed at `http://localhost:56743`.

### Stopping

```bash
docker compose down
```

### Volume Issues

If the sandbox volume has permission issues:

```bash
docker compose down -v
docker compose up --build
```

## API Usage

### Analyze a Workbook

```bash
curl -X POST http://127.0.0.1:8000/opos/analyze \
  -H "Content-Type: application/json" \
  -d '{"workbook_source": "Opos-test.xlsx"}'
```

### Health Check

```bash
curl http://127.0.0.1:8000/api/v1/health
# {"status": "ok"}
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError` | Run `uv sync` to ensure all dependencies are installed |
| Dependency conflicts | Run `uv sync --reinstall` for a clean environment |
| Docker permission errors | Run `docker compose down -v` then rebuild |
| OpenAI API errors | Verify `OPENAI_API_KEY` is set correctly in `.env` |
