This is a comprehensive, repo-agnostic **DevOps & Repository Hygiene Standard** template.

It is designed as the DevOps-specific chunk of a typical "Requirements Specification" for an engineer. It focuses on **principles and outcomes** rather than strict tool mandates, allowing the engineer to select the best tool for the specific tech stack (e.g., genericizing `ruff` to "High-Performance Linter" or `uv` to "Deterministic Package Manager").

---

# Template: DevOps & Repository Hygiene Standard

## 📋 Overview

This document defines the **mandatory** standards for DevOps practices, automation, and repository hygiene for the current project at hand (this directory).
**Goal:** To establish a robust, secure, and maintainable codebase where quality is enforced automatically via CI/CD and pre-commit hooks, regardless of the underlying technology stack.

---

## 1. Continuous Integration (CI) Pipeline

**Requirement:** A CI pipeline must be defined (e.g., GitHub Actions, GitLab CI) that enforces quality gates on every commit.

### **1.1 Triggers**

* **Pull Requests:** Must trigger on all PRs targeting the default branch (`main`/`master`).
* **Push:** Must trigger on pushes to the default branch to ensure the "Golden Copy" is always stable.
* **Draft PRs:** Should ideally run a lightweight version of the pipeline.

### **1.2 Quality Gates (Jobs)**

The pipeline must include the following parallel or dependent stages. If any stage fails, the build is marked `FAILED`.

### **1.3 Runner Environment Optimization (Disk Space Management)**

**Requirement:** For resource-intensive builds (e.g., CUDA/GPU kernels, heavy C++ compilation, or large container images), the CI environment must be "slimmed down" before the build starts to prevent Out-of-Disk (OOD) errors.

* **Workspace Pre-cleaning:** Implement a dedicated "Cleanup" step at the start of the job to remove unused pre-installed software (e.g., Android SDKs, .NET runtimes, Haskell toolchains) from the runner.
* **Disk Auditing:** Include steps to log initial and post-cleanup disk usage (`df -h`) to monitor environment health and identify bloat.
* **Tooling:** Use verified community actions (e.g., `free-disk-space`) or custom shell scripts to purge the `/opt/ghc` or `/usr/local/share/boost` directories when they are not required for the specific tech stack.
* Example: choice for removal depends on which stack is not being used in the project
'''
steps:
      - name: Free Disk Space
        uses: jlumbroso/free-disk-space@main
        with:
          tool-cache: true
          android: true
          dotnet: true
          haskell: true
          large-packages: true
          docker-images: true
'''

#### **A. Static Analysis & Formatting**

* **Linting:** Execute the strict linter appropriate for the language (e.g., `ruff`, `eslint`, `golangci-lint`). Code must be free of logic errors and unused imports.
* **Formatting:** Enforce a "zero-configuration" style guide (e.g., `prettier`, `black`, `gofmt`). The CI should check for format adherence (`--check` mode).
* **Type Checking:** If the language supports it (Python, TS, Go, Rust), strict static type checking is **mandatory** (e.g., `mypy --strict`, `tsc --noEmit`).

#### **B. Testing**

* **Unit Tests:** Execute the test suite (e.g., `pytest`, `jest`).
* **Coverage:** Generate coverage reports. A minimum coverage threshold (e.g., 80%) should be enforced where applicable.

#### **C. Build Verification**

* **Artifact/Container Build:** Ensure the application builds successfully.
* **Dependency Caching:** The CI environment must utilize caching (e.g., `actions/cache`) for package managers to minimize build times.

---

## 2. Pre-Commit Hooks (Shift-Left Security)

**Requirement:** A local hook configuration (e.g., via `pre-commit` framework or `husky`) must be present to catch issues *before* they enter the remote repository.

### **2.1 Standard Hooks**

* **Hygiene:**
* Trim trailing whitespace.
* Ensure files end with a newline.
* Validate syntax for config files (YAML, JSON, TOML).
* Prevent commit of large binaries (`check-added-large-files`).


* **Security:**
* **Secret Scanning:** Must detect accidentally committed private keys, tokens, or AWS credentials (e.g., `detect-private-key`).


* **Code Consistency:**
* Must run the **same** Linter and Formatter versions used in the CI pipeline to ensure "Local Success = CI Success."



---

## 3. Dependency Management

**Requirement:** Dependencies must be pinned, deterministic, and automatically updated.

### **3.1 Strategy**

* **Lock Files:** Commit lock files (`package-lock.json`, `uv.lock`, `go.sum`) to ensure deterministic builds across all environments.
* **Automation:** Configure an automated tool (e.g., **Dependabot**, **Renovate**) to scan for outdated packages.
* **Frequency:** Weekly or Monthly (to reduce noise).
* **Grouping:** Enable "Dependency Grouping" to bundle multiple updates (e.g., all `aws-sdk` updates) into a single Pull Request.
* **Security Updates:** Must be prioritized and applied immediately.



---

## 4. Containerization & Production Readiness

**Requirement:** If the artifact is a service, it must be containerized following the "Twelve-Factor App" methodology.

### **4.1 Dockerfile Standards**

* **Base Images:** Use lightweight, official generic images (e.g., `python:slim`, `node:alpine`, `distroless`).
* **Multi-Stage Builds:** strictly separate the **Build Stage** (compilers, dev dependencies) from the **Runtime Stage** (only compiled artifacts and runtime deps) to minimize image size.
* **Least Privilege:**
* **Do not run as Root.** Create a specific user (e.g., `appuser` with UID 1000) and switch to it using the `USER` directive.


* **Optimization:**
* leverage layer caching by copying dependency definition files (`pyproject.toml`, `package.json`) and installing dependencies *before* copying source code.


* **Health Checks:** Include a `HEALTHCHECK` instruction to validate the service is actually processing requests, not just that the process is running.

### **4.2 Runtime Configuration**

* **Process Managers:** For interpreted languages (Python, Ruby), use a production-grade application server (e.g., `gunicorn`, `puma`) instead of the default development server.
* **Signal Handling:** Ensure the app handles `SIGTERM` / `SIGINT` for graceful shutdowns.

---

## 5. Code Quality Configuration

**Requirement:** Configuration files must be explicit and committed to the repo root.

### **5.1 Configuration Manifests**

* **Centralized Config:** Where possible, consolidate configs (e.g., use `pyproject.toml` or `package.json` instead of scattered `.rc` files).
* **Strictness:**
* **Linting:** Enable rules for Bugs, Security, and Modern Best Practices (e.g., `flake8-bugbear` or equivalent).
* **Types:** Disallow "Any" types where possible.



---

## 6. Security & Sensitive Data

**Requirement:** Zero-tolerance policy for secrets in source control.

* **Gitignore:** Explicitly exclude sensitive paths:
* Environment files (`.env`).
* IDE configurations (`.idea`, `.vscode`).
* Virtual environments and build artifacts (`venv/`, `dist/`, `node_modules/`).


* **Environment Variables:** The application must load configuration via Environment Variables. A `.env.example` template must be provided for developer reference.

---

## 7. Implementation Approach

When applying this template to a repository, one must:

* Identify the primary Tech Stack.
* Select the highest-performance tooling for that stack (e.g., `uv` for Python, `pnpm` for Node).
* Generate the `.github/workflows/ci.yml`.
* Generate the `.pre-commit-config.yaml`.
* Generate the `Dockerfile` with multi-stage builds.
* Ensure no secrets are present in the history.
