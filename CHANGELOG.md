# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned

- Multi-sheet workbook support with automatic sheet detection.
- Configurable maturity brackets.
- Prometheus metrics endpoint.
- Comprehensive test suite (report generator, integration, e2e).

## [0.1.0] — 2025-06-10

### Added

- FastAPI application with factory pattern and async lifespan management.
- `POST /opos/analyze` endpoint for A/R open posts analysis.
- Health (`/api/v1/health`) and readiness (`/api/v1/ready`) probe endpoints.
- 2-node LangGraph workflow:
  - **Semantic Mapping** — GPT-4o-mini maps German column headers to semantic English keys using structured output.
  - **Report Generator** — deterministic Python logic for cumulative row detection, invoice/credit classification, maturity calculation, and cluster assignment.
- Pydantic settings with environment variable, `.env` file, and GCP Secret Manager support.
- Excel data loading from URLs or local file paths with SQLite mirroring.
- Google Cloud Storage upload for non-local environments.
- Formatted Excel output with three sheets: Original, Processed (hidden), and Analysis.
- Multi-stage Dockerfile with non-root user, layer caching, and HEALTHCHECK.
- Docker Compose configuration for local development with hot reloading.
- LangSmith tracing integration for LLM observability.
- Centralised logging configuration with third-party library noise suppression.
- Unit tests for the configuration module.
- Ruff linter/formatter configuration in `pyproject.toml`.
- Pre-commit hooks (trailing whitespace, YAML/TOML validation, ruff, secret detection).
- GitHub Actions CI pipeline (lint, test, Docker build).
