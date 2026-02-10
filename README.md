# SheetAgent

AI-powered tool for analyzing Accounts Receivable (A/R) open posts lists and generating comprehensive aging reports. SheetAgent automatically identifies German accounting column names via LLM-based semantic mapping, then uses deterministic Python logic to calculate maturity clusters and produce formatted Excel reports.

## Motivation

Financial controllers routinely receive A/R open-items exports from SAP or similar ERP systems. These exports contain German-language column headers that vary across clients and ERP configurations. Manually mapping columns, classifying rows, and computing aging brackets is tedious and error-prone.

SheetAgent solves this by:

- **Semantic understanding** — an LLM (GPT-4o-mini) reads the column headers once and returns a structured mapping.
- **Deterministic calculations** — all maturity arithmetic, row classification, and aggregation is pure Python, ensuring reproducible and auditable results.
- **Single API call** — upload an Excel file, receive the enriched workbook back.

## Documentation

| Document | Purpose |
|----------|---------|
| [Quick Start](QUICKSTART.md) | Prerequisites, installation, running locally and via Docker |
| [Architecture](ARCHITECTURE.md) | Technical design, component breakdown, Mermaid diagrams |
| [Deployment](DEPLOYMENT.md) | Production deployment strategies and environment config |
| [Roadmap](ROADMAP.md) | Milestones, completed phases, and future plans |
| [Changelog](CHANGELOG.md) | Version history following Keep a Changelog |
| [Contributing](CONTRIBUTING.md) | Contribution workflow and coding standards |

## Project Structure

```
sheetagent/
├── main.py                       # Uvicorn entry point
├── app/
│   ├── app.py                    # FastAPI application factory
│   ├── api/endpoints/
│   │   ├── health.py             # Liveness & readiness probes
│   │   └── opos.py               # POST /opos/analyze endpoint
│   ├── core/
│   │   ├── config.py             # Pydantic settings (env + GCP Secret Manager)
│   │   ├── logging_config.py     # Centralised logging setup
│   │   ├── prompt_manager.py     # LLM prompt templates for semantic mapping
│   │   └── report_generator.py   # Deterministic A/R aging calculations
│   ├── dataset/
│   │   └── dataloader.py         # Excel loading, SQLite creation
│   ├── graph/
│   │   ├── graph.py              # 2-node LangGraph workflow
│   │   └── state.py              # GraphState TypedDict
│   ├── services/
│   │   └── analysis_service.py   # Orchestrator: temp dirs, graph run, output
│   └── utils/
│       ├── gcs.py                # Google Cloud Storage upload
│       └── semantic_schema.py    # Pydantic model for structured LLM output
├── tests/
│   └── core/
│       └── test_config.py        # Unit tests for configuration
├── Dockerfile                    # Multi-stage container build
├── docker-compose.yml            # Local development orchestration
└── pyproject.toml                # Project metadata and dependencies (uv)
```

## Key Dependencies

| Dependency | Role |
|------------|------|
| **LangGraph** (LangChain) | Stateful workflow orchestration |
| **OpenAI GPT-4o-mini** | Semantic column mapping with structured output |
| **Pandas & OpenPyXL** | Excel I/O and data processing |
| **FastAPI** | REST API framework |
| **Pydantic** | Type-safe settings and structured LLM outputs |
| **Google Cloud Storage** | Output file hosting in non-local environments |

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
