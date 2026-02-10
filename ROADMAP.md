# Roadmap

This document outlines the milestones, completed phases, and planned future development for SheetAgent.

## Completed

### Phase 1 — Core Architecture

- FastAPI application with factory pattern and lifespan management.
- Pydantic-based settings with `.env` and GCP Secret Manager integration.
- Excel data loading via Pandas with SQLite mirroring.
- Centralised logging configuration.

### Phase 2 — 2-Node Deterministic Workflow

- LangGraph `StateGraph` with linear `semantic_mapping → report_generator` flow.
- GPT-4o-mini semantic column mapping with structured output (`SemanticSchema`).
- Deterministic A/R aging report generation:
  - Cumulative row detection via running-sum matching and keyword checks.
  - Invoice and credit row classification.
  - Maturity calculation and cluster assignment (Not mature, 1–30, 31–60, >60 days).
  - Formatted Analysis sheet with currency-aware formatting.

### Phase 3 — Deployment Infrastructure

- Multi-stage Dockerfile with non-root user and layer caching.
- Docker Compose for local development with hot reloading.
- Google Cloud Storage integration for non-local output.
- Health and readiness endpoints.

### Phase 4 — Quality & DevOps

- Unit tests for configuration module.
- Ruff linter and formatter integration.
- Pre-commit hooks for code quality enforcement.
- GitHub Actions CI pipeline (lint, test, Docker build).

## Planned

### Phase 5 — Enhanced Analysis

- Support for multi-sheet workbooks with automatic sheet detection.
- Configurable maturity brackets (currently hard-coded).
- Additional output formats (PDF summary, CSV export).
- Batch processing endpoint for multiple workbooks.

### Phase 6 — Observability

- Prometheus metrics endpoint for request latency, error rates, and LLM token usage.
- Grafana dashboard templates.
- Structured JSON logging for cloud log aggregation.

### Phase 7 — Robustness

- Comprehensive test suite: unit tests for report generator, integration tests for the full graph, end-to-end API tests.
- Input validation for malformed Excel files (missing columns, empty sheets).
- Retry logic for transient OpenAI API failures.
- Rate limiting on the `/opos/analyze` endpoint.

### Phase 8 — Multi-Provider LLM Support

- Abstract the LLM interface to support providers beyond OpenAI (Anthropic, Google Gemini).
- Model selection via configuration rather than hard-coding.
