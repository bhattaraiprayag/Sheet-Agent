# Contributing

Contributions are welcome. This document covers the development workflow and coding standards for SheetAgent.

## Development Setup

1. Clone the repository and install dependencies:
   ```bash
   git clone <repository-url>
   cd Sheet-Agent
   uv sync --group dev
   ```

2. Install pre-commit hooks:
   ```bash
   uv run pre-commit install
   ```

3. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

## Workflow

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature
   ```
2. Make changes and ensure all checks pass locally.
3. Commit with a clear, descriptive message.
4. Open a Pull Request against `main`.

## Code Standards

### Style

- **Linter / Formatter**: [Ruff](https://docs.astral.sh/ruff/) — configured in `pyproject.toml`.
- **PEP 8** compliance is enforced automatically.
- **Type annotations** are required on all function signatures.
- **Docstrings** are required on all public functions and classes.

### Running Checks

```bash
# Lint
uv run ruff check .

# Format check
uv run ruff format --check .

# Auto-fix lint issues
uv run ruff check --fix .

# Auto-format
uv run ruff format .

# Run tests
uv run pytest

# Run all pre-commit hooks
uv run pre-commit run --all-files
```

### Commit Hygiene

- Pre-commit hooks run automatically on `git commit`. They enforce:
  - Trailing whitespace removal.
  - File ending with newline.
  - YAML and TOML syntax validation.
  - No large files committed.
  - No private keys committed.
  - Ruff linting and formatting.

## Testing

- Tests live in the `tests/` directory, mirroring the `app/` structure.
- Use `pytest` as the test runner.
- Mock external services (OpenAI, GCS) in tests — never make real API calls.

## Project Dependencies

- **Runtime** dependencies are listed under `[project.dependencies]` in `pyproject.toml`.
- **Development** dependencies (ruff, pytest, pre-commit) are in `[dependency-groups.dev]`.
- Always use `uv sync` and `uv add` to manage dependencies. Do not edit `uv.lock` manually.
