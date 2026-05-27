# OpenTelemetry Demo - Local Runbook Overview

Quick-start guide for running the OpenTelemetry Demo locally.

## Prerequisites

- Docker and Docker Compose installed
- Make installed
- Node.js (for frontend development)
- Python 3.x (for linting and validation tools)
- Go 1.21+ (for backend services)
- Java 21+ (for Ad service)
- Gradle (for Ad service build)

## Quick Start

### Start Full Demo Stack

```bash
# Full stack with all services
make start

# Minimal stack (fewer services for development)
make start-minimal
```

Once running, access:
- Demo UI: http://localhost:8080
- Jaeger UI: http://localhost:8080/jaeger/ui
- Grafana: http://localhost:8080/grafana/
- Load Generator: http://localhost:8080/loadgen/
- Feature Flags: http://localhost:8080/feature/

### Stop Demo

```bash
make stop
```

## Build Images

```bash
# Build all service Docker images
make build

# Build and push images to registry
make build-and-push

# Build multiplatform images (linux/amd64, linux/arm64)
make build-multiplatform
```

## Run Tests

```bash
# Run all tests (frontend + trace-based)
make run-tests

# Run only trace-based tests
make run-tracetesting

# Run trace tests for specific services
make run-tracetesting SERVICES_TO_TEST="ad cart payment"
```

## Common Development Tasks

### Lint and Check

```bash
# Run all checks (spelling, markdown, license, links)
make check

# Markdown linting only
make markdownlint

# Spell check
make misspell

# YAML linting
make yamllint

# License header check
make checklicense

# Fix auto-fixable issues
make fix

# Fix spelling errors in place
make misspell-correction
```

### Protobuf

```bash
# Generate protobuf files (IDE method, no Docker)
make generate-protobuf

# Generate protobuf files using Docker
make docker-generate-protobuf
```

### Service Management

```bash
# Restart a single service (e.g., frontend)
make restart service=frontend

# Rebuild and restart a service
make redeploy service=frontend
```

### Kubernetes

```bash
# Generate Kubernetes manifests from docker-compose
make generate-kubernetes-manifests
```

## Development Notes

- The Makefile uses `docker compose` command (v2+)
- Environment configuration is in `.env` and `.env.override`
- On ARM64 macOS (M1/M2), special Java settings are applied automatically
- All service images are configured in docker-compose.yml with health checks

## Next Steps

See `detail.md` for comprehensive command reference including per-service testing, building, and linting commands.
