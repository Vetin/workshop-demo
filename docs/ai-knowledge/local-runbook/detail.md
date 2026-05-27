# OpenTelemetry Demo - Comprehensive Command Reference

Complete reference for all runnable commands in the OpenTelemetry Demo repository.

## Repository Structure

```
opentelemetry-demo/
├── Makefile                           # Main orchestration (all commands start here)
├── docker-compose.yml                 # Full stack configuration
├── docker-compose.minimal.yml         # Minimal stack (faster startup)
├── docker-compose-tests.yml           # Test services and tools
├── src/                               # Service source code
│   ├── accounting/                    # C# (.NET) service
│   ├── ad/                            # Java (Gradle) service
│   ├── cart/                          # Go service
│   ├── checkout/                      # Go service
│   ├── currency/                      # Go service
│   ├── email/                         # Python service
│   ├── fraud-detection/               # C# (.NET) service
│   ├── frontend/                      # TypeScript/Next.js (Node.js)
│   ├── frontend-proxy/                # Nginx
│   ├── llm/                           # Python service
│   ├── load-generator/                # Python service
│   ├── payment/                       # Node.js
│   ├── product-catalog/               # Go service
│   ├── product-reviews/               # Python service
│   ├── quote/                         # C# (.NET) service
│   ├── recommendation/                # Python service
│   └── shipping/                      # Rust service
├── test/
│   └── tracetesting/                  # Tracetest-based tests
└── .github/workflows/                 # CI/CD workflows
```

## Full Command Reference by Category

### DOCKER COMPOSE & STACK MANAGEMENT

**Source**: Makefile (lines 184-249)

| Command | Purpose | Duration | Notes |
|---------|---------|----------|-------|
| `make start` | Start full demo stack in background | 1-2 min | Creates all 28 services, accessible at http://localhost:8080 |
| `make start-minimal` | Start minimal stack (faster) | 30-60 sec | Reduced service set for lightweight development |
| `make stop` | Stop and clean up all services | 30 sec | Removes containers, networks, and volumes |
| `make restart service=<name>` | Restart a single service (no rebuild) | 10-30 sec | Example: `make restart service=frontend` |
| `make redeploy service=<name>` | Rebuild and restart a service | 2-5 min | Example: `make redeploy service=payment` |

**Available Services** (from docker-compose config):
- Core: accounting, ad, cart, checkout, currency, email, fraud-detection, frontend
- Services: llm, payment, product-catalog, product-reviews, quote, recommendation, shipping
- Infrastructure: frontend-proxy, flagd, flagd-ui, grafana, jaeger, kafka, otel-collector, postgresql, prometheus, opensearch
- Utilities: load-generator, image-provider, valkey-cart

### BUILD COMMANDS

**Source**: Makefile (lines 95-125)

| Command | Purpose | Duration | Cost |
|---------|---------|----------|------|
| `make build` | Build all service Docker images | 10-20 min | High - rebuilds all services |
| `make build-and-push` | Build and push to registry | 15-30 min | High - requires Docker auth |
| `make build-multiplatform` | Build linux/amd64 + linux/arm64 | 20-40 min | Very High - multiplatform build |
| `make build-multiplatform-and-push` | Build and push multiplatform | 25-45 min | Very High |
| `make create-multiplatform-builder` | Create buildx builder (one-time setup) | 1 min | Setup only |
| `make remove-multiplatform-builder` | Remove buildx builder | 10 sec | Cleanup |
| `make clean-images` | Remove demo Docker images | 10 sec | Safe - removes local images only |

**Service Dockerfiles**:
```
src/accounting/Dockerfile              C# service
src/ad/Dockerfile                      Java service (uses Gradle build)
src/cart/src/Dockerfile                Go service
src/checkout/Dockerfile                Go service
src/currency/Dockerfile                Go service
src/email/Dockerfile                   Python service
src/fraud-detection/Dockerfile         C# service
src/frontend/Dockerfile                TypeScript/Next.js service
src/frontend/Dockerfile.cypress        Frontend test container
src/frontend-proxy/Dockerfile          Nginx proxy
src/flagd-ui/Dockerfile                Feature flags UI
src/image-provider/Dockerfile          Image server
src/kafka/Dockerfile                   Kafka setup
src/llm/Dockerfile                     Python LLM service
src/load-generator/Dockerfile          Python load generator
src/opensearch/Dockerfile              Opensearch setup
src/payment/Dockerfile                 Node.js payment service
src/product-catalog/Dockerfile         Go service
src/product-reviews/Dockerfile         Python service
src/quote/Dockerfile                   C# service
src/recommendation/Dockerfile          Python service
src/shipping/Dockerfile                Rust service
test/tracetesting/Dockerfile           Tracetest runner
```

### TEST COMMANDS

**Source**: Makefile (lines 137-145) + test/tracetesting/

| Command | Purpose | Duration | Scope |
|---------|---------|----------|-------|
| `make run-tests` | Run all tests (frontend + trace-based) | 10-15 min | Full suite |
| `make run-tracetesting` | Run trace-based tests (all services) | 8-12 min | Tracetest only |
| `make run-tracetesting SERVICES_TO_TEST="ad cart payment"` | Test specific services | 2-5 min | Filtered |

**Test Infrastructure**:
```
test/tracetesting/
├── Dockerfile                         Tracetest runner image
├── run.bash                           Main test orchestration script
├── cli-config.yml                     Tracetest CLI configuration
├── tracetest-config.yaml              Tracetest server configuration
├── tracetest-provision.yaml           Service/test provisioning
├── otelcol-config-tracetest.yml       Collector config for tests
├── ad/all.yaml                        Ad service test suite
├── cart/all.yaml                      Cart service test suite
├── checkout/all.yaml                  Checkout service test suite
├── currency/all.yaml                  Currency service test suite
├── email/all.yaml                     Email service test suite
├── frontend/all.yaml                  Frontend test suite
├── payment/all.yaml                   Payment service test suite
├── product-catalog/all.yaml           Product catalog test suite
├── product-reviews/all.yaml           Product reviews test suite
├── recommendation/all.yaml            Recommendation test suite
└── shipping/all.yaml                  Shipping service test suite
```

**Available Services for Trace Testing**:
- ad, cart, currency, checkout, frontend, email, payment, product-catalog, product-reviews, recommendation, shipping

**Docker Compose Test Services**:
- `frontendTests` - Cypress-based frontend tests (docker-compose-tests.yml line 14)
- `traceBasedTests` - Tracetest-based trace validation (docker-compose-tests.yml line 31)
- `tracetest-server` - Tracetest backend (docker-compose-tests.yml line 96)
- `tracetest-postgres` - Tracetest database (docker-compose-tests.yml line 123)

### FRONTEND-SPECIFIC COMMANDS

**Source**: src/frontend/package.json

**Frontend Build Location**: src/frontend/

| Command | Purpose | Location |
|---------|---------|----------|
| `npm run dev` | Start frontend dev server (with telemetry) | src/frontend/ |
| `npm run build` | Build Next.js production bundle | src/frontend/ |
| `npm start` | Start frontend server (production) | src/frontend/ |
| `npm run lint` | Run Next.js linter (ESLint) | src/frontend/ |
| `npm run cy:open` | Open Cypress test runner (interactive) | src/frontend/ |
| `npm run grpc:generate` | Generate TypeScript gRPC bindings | src/frontend/ |

**Frontend Test Container**: src/frontend/Dockerfile.cypress
- Used in `docker-compose-tests.yml` as `frontendTests`
- Runs Cypress end-to-end tests

### REACT NATIVE APP COMMANDS

**Source**: src/react-native-app/package.json

| Command | Purpose |
|---------|---------|
| `npm start` | Start Expo development server |
| `npm run android` | Build and run on Android device/emulator |
| `npm run ios` | Build and run on iOS device/simulator |
| `npm run web` | Run as web app via Expo |
| `npm test` | Run Jest tests (watch mode) |
| `npm run lint` | Run ESLint with Expo presets |
| `npm run reset-project` | Reset project state |

### PAYMENT SERVICE (Node.js) COMMANDS

**Source**: src/payment/package.json

| Command | Purpose |
|---------|---------|
| `npm start` | Start payment service with OpenTelemetry instrumentation |

No other npm scripts defined; service runs as Docker container in demo.

### LINTING, CHECKING & VALIDATION COMMANDS

**Source**: Makefile (lines 31-94)

| Command | Purpose | Duration | Cost |
|---------|---------|----------|------|
| `make check` | Run all checks (spell, markdown, license, links) | 2-3 min | Low |
| `make misspell` | Check for spelling errors in docs | 10 sec | Low |
| `make misspell-correction` | Auto-fix spelling errors | 10 sec | Low |
| `make markdownlint` | Lint all markdown files (.md) | 30 sec | Low |
| `make yamllint` | Lint all YAML files | 30 sec | Low |
| `make checklicense` | Verify license headers on source | 30 sec | Low |
| `make checklinks` | Verify documentation links | 1-2 min | Low |
| `make install-tools` | Install misspell, npm dependencies | 1 min | One-time |
| `make install-yamllint` | Install yamllint via pip | 30 sec | One-time |
| `make addlicense` | Add license headers to files | 30 sec | Low |
| `make fix` | Auto-fix auto-fixable issues | 30 sec | Low |

**Tools Used**:
- misspell: Spell checking for documentation
- markdownlint: Markdown linting (config: .markdownlint.yaml)
- yamllint: YAML validation (config: .yamllint or defaults)
- @kt3k/license-checker: License header verification
- @umbrelladocs/linkspector: Documentation link validation

### PROTOBUF CODE GENERATION

**Source**: Makefile (lines 146-172)

| Command | Purpose | Notes |
|---------|---------|-------|
| `make generate-protobuf` | Generate proto files locally | Uses ide-gen-proto.sh, requires protoc installed |
| `make docker-generate-protobuf` | Generate proto files in Docker | Recommended, more reliable |
| `make clean` | Remove all generated proto files | Cleans protobuf outputs |

**Generated Protobuf Files**:
```
src/checkout/genproto/oteldemo/             Go checkout service
src/product-catalog/genproto/oteldemo/      Go product-catalog service
src/recommendation/demo_pb2*                 Python recommendation service
src/frontend/protos/demo.ts                  TypeScript frontend service
```

**Proto Source**: pb/demo.proto (shared across all services)

### CI/CD INTEGRATION TEST COMMANDS

**Source**: .github/workflows/

| Workflow | Trigger | Commands |
|----------|---------|----------|
| checks.yml | Push to main, PR, manual | `make markdownlint`, `make yamllint`, `make misspell`, `make checklicense`, `make install-tools`, image build |
| run-integration-tests.yml | PR approval | `make build && docker system prune -f && make run-tracetesting` |
| component-build-images.yml (reusable) | Called by other workflows | `make clean docker-generate-protobuf`, `make check-clean-work-tree`, docker build matrix |

**Expensive Commands** (avoid in every task):
- `make build` - 10-20 minutes
- `make build-multiplatform*` - 20-45 minutes
- `make run-tests` - 10-15 minutes
- `make run-tracetesting` - 8-12 minutes (without specific service filtering)

## Environment Files

**Configuration**:
```
.env                     Base environment config (5KB)
.env.override            Override settings for local development
.env.arm64               ARM64-specific Java options (macOS M1/M2)
```

**Key Environment Variables**:
- OTEL_COLLECTOR_HOST, OTEL_COLLECTOR_PORT_HTTP
- OTEL_EXPORTER_OTLP_ENDPOINT
- Various service ports (AD_PORT, CART_PORT, etc.)
- Database credentials (POSTGRES_HOST, POSTGRES_DB, etc.)
- Docker image names and versions (IMAGE_NAME, DEMO_VERSION)

## Service-Specific Details

### Go Services (Cart, Checkout, Currency, Product Catalog)
- Build via Dockerfile only
- Source: src/{service}/Dockerfile
- Testing: Trace-based tests only via Tracetest

### Python Services (Email, Recommendation, LLM, Load Generator, Product Reviews)
- Build via Dockerfile
- Source: src/{service}/Dockerfile
- One test file found: src/checkout/money/money_test.go (Go unit test)

### Java Service (Ad)
- Build via Gradle (src/ad/build.gradle)
- Dockerfile: src/ad/Dockerfile
- Requires Java 21+, Gradle
- Uses OTEL Java Agent for instrumentation

### C# Services (Accounting, Fraud Detection, Quote)
- Build via Dockerfile
- Database: PostgreSQL connection strings
- .NET runtime in container

### Node.js Services (Frontend, Payment)
- Frontend: Full npm build system with dev/prod modes
- Payment: Simple startup only (npm start)

### Rust Service (Shipping)
- Build via Dockerfile
- Source: src/shipping/

### React Native App
- Package.json in src/react-native-app/
- Uses Expo for development
- Can run on Android, iOS, Web

## Quick Workflow Examples

### Local Development (Frontend)
```bash
# Terminal 1: Start minimal backend stack
make start-minimal

# Terminal 2: Develop frontend with live reload
cd src/frontend
npm install
npm run dev

# Access at http://localhost:3000 (Next.js dev) or http://localhost:8080 (via proxy)
```

### Service Development (e.g., Payment Service)
```bash
# Update code
# Rebuild and restart
make redeploy service=payment

# Check logs
docker logs payment -f
```

### Testing Workflow
```bash
# Start full stack
make start

# Wait for services to be ready (30-60 seconds)

# Run specific service trace tests
make run-tracetesting SERVICES_TO_TEST="payment checkout"

# Run all tests
make run-tests
```

### CI/CD Validation
```bash
# Run all checks (what CI does)
make check

# Build images (what CI does)
make build

# Cleanup after (what CI does)
make stop
```

### Protobuf Updates
```bash
# Update pb/demo.proto
# Regenerate bindings
make docker-generate-protobuf

# Verify no uncommitted changes
make check-clean-work-tree

# Build updated services
make build
```

## Recommended Gate Levels

Use these gate configurations for different test scenarios:

### FAST Gate (2-3 minutes)
- Linting: `make check` OR individual checks
- Spell check: `make misspell`
- Markdown: `make markdownlint`
- License: `make checklicense`
- YAML: `make yamllint`

Use for: Pre-commit, pull request validation, quick feedback

### MEDIUM Gate (5-8 minutes)
- All FAST gate checks
- Protobuf generation: `make docker-generate-protobuf`
- Protobuf verification: `make check-clean-work-tree`
- Docker image build: `make build`

Use for: Pre-merge validation, feature branch validation

### FULL Gate (30-60 minutes)
- All MEDIUM gate checks
- Trace-based tests: `make run-tracetesting`
- Frontend tests: `make run-tests`
- Multiplatform builds: `make build-multiplatform`

Use for: Release preparation, major feature validation, after approval

## File Reference Summary

| File | Purpose | Key Content |
|------|---------|-------------|
| Makefile | Command orchestration | 253 lines, 30+ targets |
| docker-compose.yml | Full stack definition | 28 services, environment config |
| docker-compose.minimal.yml | Minimal stack | Reduced service set |
| docker-compose-tests.yml | Test infrastructure | Frontend tests, Tracetest setup |
| .env | Base configuration | 5080 bytes |
| .env.override | Local overrides | 388 bytes |
| .env.arm64 | ARM64 Java options | 27 bytes |
| pb/demo.proto | gRPC definitions | Shared across services |
| .github/workflows/checks.yml | CI validation | Linting and building |
| .github/workflows/run-integration-tests.yml | Integration tests | PR approval trigger |

## Notes & Best Practices

1. **Always run `make stop` before `make start`** to ensure clean state
2. **Use `make start-minimal` for faster local development** cycles
3. **Run `make check` before committing** to catch issues early
4. **Use service-specific `make redeploy`** instead of full rebuild for fast iteration
5. **Docker Compose v2+ required** (uses `docker compose` not `docker-compose`)
6. **Protobuf changes require rebuild** of affected services
7. **Trace tests require full stack running** - start with `make start` first
8. **Frontend can be developed separately** with `npm run dev` locally
9. **Check `.env` files for configuration** before making assumptions
10. **Use absolute paths** in scripts; working directory varies between bash calls

