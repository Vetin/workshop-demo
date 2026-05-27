# OpenTelemetry Demo Architecture - Detailed

## Repository Structure

```
opentelemetry-demo/
├── .claude/                                    # Claude Code configuration & agents
├── .github/                                    # GitHub CI/CD workflows
├── .sdd/                                       # Spec-Driven Development configs
├── CLAUDE.md                                   # Project contribution rules
├── Makefile                                    # Build & deployment automation
├── README.md                                   # Main documentation
├── CONTRIBUTING.md                             # Contribution guidelines
├── CHANGELOG.md                                # Version history
├── LICENSE                                     # Apache 2.0
│
├── docker-compose.yml                          # Full deployment (30 services)
├── docker-compose.minimal.yml                  # Reduced deployment (core only)
├── docker-compose-tests.yml                    # Test execution environment
├── docker-compose-tests_include-override.yml   # Test overrides
├── docker-gen-proto.sh                         # Proto generation (Docker)
├── ide-gen-proto.sh                            # Proto generation (IDE)
│
├── .env                                        # Environment variables (main)
├── .env.override                               # Environment overrides
├── .env.arm64                                  # ARM64 macOS Java workaround
├── .dockerignore                               # Docker exclusions
├── .gitignore                                  # Git exclusions
├── .markdownlint.yaml                          # Markdown linting
├── .yamllint                                   # YAML linting
├── .linkspector.yml                            # Link checking
│
├── pb/                                         # Protocol Buffer contracts
│   └── demo.proto                              # gRPC service definitions
│
├── src/                                        # Application services
│   ├── accounting/                             # .NET/C# Kafka consumer
│   ├── ad/                                     # Java (Gradle) Spring Boot
│   ├── cart/                                   # .NET/C# ASP.NET Core
│   ├── checkout/                               # Go gRPC orchestrator
│   ├── currency/                               # C++ currency converter
│   ├── email/                                  # Ruby mail simulator
│   ├── flagd/                                  # Feature flag store (JSON config)
│   ├── flagd-ui/                               # Elixir Phoenix flag UI
│   ├── fraud-detection/                        # Java (Gradle) Kafka consumer
│   ├── frontend/                               # React Next.js e-commerce UI
│   ├── frontend-proxy/                         # Envoy reverse proxy
│   ├── image-provider/                         # Nginx static content
│   ├── llm/                                    # Python mock LLM
│   ├── load-generator/                         # Python Locust traffic generator
│   ├── otel-collector/                         # OTel Collector configuration
│   ├── payment/                                # Node.js Express payment service
│   ├── product-catalog/                        # Go gRPC catalog
│   ├── product-reviews/                        # Python review aggregation
│   ├── quote/                                  # PHP shipping cost calculator
│   ├── recommendation/                         # Python recommender engine
│   ├── shipping/                               # Rust shipment tracking
│   ├── react-native-app/                       # React Native mobile example
│   │
│   ├── grafana/                                # Grafana configuration (dashboards)
│   ├── jaeger/                                 # Jaeger configuration (query)
│   ├── kafka/                                  # Kafka broker configuration
│   ├── opensearch/                             # OpenSearch log storage config
│   ├── postgresql/                             # PostgreSQL database config
│   └── prometheus/                             # Prometheus server config
│
├── test/                                       # Test suites
│   ├── README.md                               # Testing documentation
│   └── tracetesting/                           # Tracetest-based trace validation
│       ├── ad/                                 # Ad service tests
│       ├── cart/                               # Cart service tests
│       ├── checkout/                           # Checkout service tests
│       ├── currency/                           # Currency service tests
│       ├── email/                              # Email service tests
│       ├── frontend/                           # Frontend tests (Playwright/Jest)
│       ├── payment/                            # Payment service tests
│       ├── product-catalog/                    # Product catalog tests
│       ├── product-reviews/                    # Product reviews tests
│       ├── recommendation/                     # Recommendation service tests
│       ├── shipping/                           # Shipping service tests
│       ├── Dockerfile                          # Tracetest runner image
│       ├── cli-config.yml                      # Tracetest CLI config
│       ├── otelcol-config-tracetest.yml        # Collector config for tests
│       ├── tracetest-config.yaml               # Test runner config
│       ├── tracetest-provision.yaml            # Test provisioning
│       └── run.bash                            # Test orchestration script
│
├── kubernetes/                                 # Kubernetes/Helm deployment
│   └── opentelemetry-demo.yaml                 # Generated K8s manifests
│
├── docs/                                       # Documentation
│   ├── ai-knowledge/                           # AI agent knowledge base
│   │   ├── architecture/                       # THIS DIRECTORY
│   │   │   ├── overview.md                     # High-level architecture
│   │   │   └── detail.md                       # Detailed structure
│   │   ├── communication/                      # Service interactions
│   │   ├── frontend/                           # Frontend architecture
│   │   ├── local-runbook/                      # Local setup guide
│   │   ├── observability/                      # OTel patterns
│   │   ├── services/                           # Service inventory
│   │   ├── testing/                            # Test strategies
│   │   └── ui-kit/                             # Frontend components
│   └── features/                               # Feature documentation
│
├── specs/                                      # Specification-Driven Development
│   └── features/                               # Feature specifications
│
├── scripts/                                    # Utility scripts
├── internal/                                   # Build tooling (internal use)
│   └── tools/
│       ├── go.mod                              # Go tools dependencies
│       ├── sanitycheck.py                      # Validation script
│       └── tools.go                            # Tool imports
│
├── third_party/                                # Third-party tools & harness
│   └── ai-harness/                             # AI agent framework
│
└── screenshots/                                # Screenshot assets
```

## Service Breakdown by Language

### Go (2 services)
- **checkout** (`src/checkout/`)
  - Location: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/checkout/`
  - gRPC server on port 5050
  - Generated code: `genproto/oteldemo/demo.pb.go`, `demo_grpc.pb.go`
  - Dependencies: gRPC, protobuf, OTLP SDK

- **product-catalog** (`src/product-catalog/`)
  - Location: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/product-catalog/`
  - gRPC server on port 3550
  - Generated code: `genproto/oteldemo/demo.pb.go`, `demo_grpc.pb.go`
  - Dependencies: gRPC, protobuf, OTLP SDK

### Java (2 services)
- **ad** (`src/ad/`)
  - Location: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/ad/`
  - Spring Boot gRPC service on port 8080
  - Build: Gradle wrapper (`build.gradle`)
  - Dependencies: Spring Boot, gRPC, Java Agent instrumentation
  - JDK: 21+ required

- **fraud-detection** (`src/fraud-detection/`)
  - Location: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/fraud-detection/`
  - Spring Boot Kafka consumer
  - Build: Gradle KTS (`build.gradle.kts`)
  - Dependencies: Spring Boot, Kafka consumer, gRPC

### Python (4 services)
- **llm** (`src/llm/`)
  - Location: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/llm/`
  - FastAPI server on port 8000
  - Mock OpenAI API endpoint: `POST /v1/chat/completions`
  - Dependencies: FastAPI, OpenTelemetry SDK, pydantic

- **load-generator** (`src/load-generator/`)
  - Location: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/load-generator/`
  - Locust load testing framework on port 8089
  - Web UI: `http://localhost:8080/loadgen/`
  - Simulates realistic e-commerce user journeys

- **product-reviews** (`src/product-reviews/`)
  - Location: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/product-reviews/`
  - FastAPI gRPC service on port 8000
  - Generated code: `demo_pb2.py`, `demo_pb2_grpc.py`
  - Calls LLM service for AI summaries
  - Dependencies: gRPC, protobuf, FastAPI, OpenAI instrumentation

- **recommendation** (`src/recommendation/`)
  - Location: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/recommendation/`)
  - FastAPI gRPC service on port 8000
  - Generated code: `demo_pb2.py`, `demo_pb2_grpc.py`
  - Dependencies: gRPC, protobuf, FastAPI

### .NET/C# (2 services)
- **accounting** (`src/accounting/`)
  - Location: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/accounting/`
  - ASP.NET Core service consuming Kafka topics
  - Build: `Accounting.csproj` (dotnet CLI)
  - Database: PostgreSQL
  - Dependencies: .NET 8.0, Kafka consumer, EntityFramework Core, OTel SDK

- **cart** (`src/cart/`)
  - Location: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/cart/`
  - ASP.NET Core gRPC service on port 7070
  - Cache: Valkey (Redis-compatible)
  - Build: `cart.csproj` (dotnet CLI)
  - Dependencies: .NET 8.0, Valkey client, OTel SDK

### Node.js (1 service)
- **payment** (`src/payment/`)
  - Location: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/payment/`
  - Express gRPC service on port 8080
  - Build: npm/TypeScript
  - Generated code: `demo_pb.js` (generated to `/pb/`)
  - Dependencies: Express, gRPC, protobuf, OpenTelemetry SDK

### Rust (1 service)
- **shipping** (`src/shipping/`)
  - Location: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/shipping/`
  - Actix-web gRPC service on port 8080
  - Build: Cargo (`Cargo.toml`)
  - Dependencies: Tokio, tonic gRPC, OTel SDK

### PHP (1 service)
- **quote** (`src/quote/`)
  - Location: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/quote/`
  - HTTP server on port 8800
  - Manual + automatic instrumentation
  - Build: Docker multi-stage (Dockerfile)
  - Dependencies: PHP 8.1+, OTel SDK, cURL

### C++ (1 service)
- **currency** (`src/currency/`)
  - Location: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/currency/`
  - gRPC server on port 50051
  - Build: C++ compiler with gRPC generation
  - Dependencies: gRPC, Abseil

### Ruby (1 service)
- **email** (`src/email/`)
  - Location: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/email/`
  - HTTP server on port 8080
  - Build: Bundler (`Gemfile`)
  - Dependencies: Ruby 3.4, OTel SDK, Puma

### Elixir (1 service)
- **flagd-ui** (`src/flagd-ui/`)
  - Location: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/flagd-ui/`
  - Phoenix LiveView web app on port 4000
  - Build: Mix (`mix.exs`)
  - Feature flag management UI
  - Dependencies: Elixir 1.14+, Phoenix 1.7+, OTel SDK

### React/TypeScript (2 services)
- **frontend** (`src/frontend/`)
  - Location: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/frontend/`
  - Next.js 14 + React on port 3000
  - API routes call backend services
  - Build: npm/TypeScript
  - Generated code: `protos/demo.ts`
  - Dependencies: Next.js, React 18, protobuf.js, OTel SDK

- **react-native-app** (`src/react-native-app/`)
  - Location: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/react-native-app/`
  - React Native mobile app example
  - Targets: iOS/Android
  - Build: Expo + custom Dockerfile
  - Dependencies: React Native, TypeScript, Expo

### Infrastructure Services (No Code)
- **flagd** (`src/flagd/`)
  - JSON configuration only: `demo.flagd.json`
  - OpenFeature compatible feature flag provider
  - Launched as OCI container (not local build)

- **frontend-proxy** (`src/frontend-proxy/`)
  - Envoy proxy configuration only
  - Reverse proxy for web UIs
  - Config: `envoy.tmpl.yaml`

- **otel-collector** (`src/otel-collector/`)
  - Configuration only (launched as OCI container)
  - Main config: `otelcol-config.yml`
  - Extras config: `otelcol-config-extras.yml`
  - No code generation

- **image-provider** (`src/image-provider/`)
  - Nginx config for static content serving
  - Config: `nginx.conf.template`
  - OTel-instrumented Nginx image

### Database/Message Services (Container-based)
- **kafka** - Apache Kafka message broker
- **postgresql** - PostgreSQL relational database
- **opensearch** - OpenSearch log storage
- **jaeger** - Jaeger tracing backend
- **prometheus** - Prometheus metrics server
- **grafana** - Grafana dashboard UI

## Proto/Contract Files

### Main Proto Definition
- **Path**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/pb/demo.proto`
- **Defines**: gRPC services for checkout, product-catalog, recommendation, product-reviews, etc.
- **Compiler Targets**: Go, Python, Node.js, Java (via plugins)

### Generated Code Locations
```
src/checkout/genproto/oteldemo/
  ├── demo.pb.go                    # Go protobuf
  └── demo_grpc.pb.go               # Go gRPC stubs

src/product-catalog/genproto/oteldemo/
  ├── demo.pb.go
  └── demo_grpc.pb.go

src/recommendation/
  ├── demo_pb2.py                   # Python protobuf
  └── demo_pb2_grpc.py

src/product-reviews/
  ├── demo_pb2.py
  └── demo_pb2_grpc.py

src/frontend/protos/
  └── demo.ts                        # TypeScript protobuf.js

src/payment/
  └── (generated to ../pb/ directory)
```

### Generation Scripts
- **IDE-based**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/ide-gen-proto.sh`
- **Docker-based**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/docker-gen-proto.sh`
- **Makefile target**: `make generate-protobuf` or `make docker-generate-protobuf`
- **Cleanup**: `make clean` removes all generated code

## Observability Configuration

### OpenTelemetry Collector
- **Config**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/otel-collector/otelcol-config.yml`
- **Port (gRPC)**: 4317
- **Port (HTTP)**: 4318
- **Receivers**:
  - OTLP (gRPC, HTTP)
  - Docker stats
  - PostgreSQL metrics
  - Valkey (Redis) metrics
  - Nginx HTTP checks
  - Host metrics (CPU, memory, disk, filesystem)

- **Processors**:
  - memory_limiter
  - resourcedetection (env, docker, system)
  - transform (span name normalization)

- **Exporters**:
  - OTLP -> Jaeger (traces)
  - OTLP HTTP -> Prometheus (metrics)
  - OpenSearch (logs)
  - Debug (console output)

- **Connectors**:
  - spanmetrics (converts trace spans to latency metrics)

### Jaeger Configuration
- **Container Image**: OTEL Jaeger (all-in-one)
- **UI Port**: 16686 (proxied via frontend-proxy to `/jaeger/ui/`)
- **Trace Backend**: Stored in-memory (configurable)
- **Storage**: Supports multiple backends (Elasticsearch, BadgerDB, etc.)

### Prometheus Configuration
- **Container Image**: prom/prometheus
- **Port**: 9090
- **Scrape Targets**: OTLP exporter from collector
- **Storage**: Time-series data in prometheus container volume
- **Retention**: Configurable

### Grafana Configuration
- **Container Image**: grafana/grafana
- **Port**: 3000 (proxied via frontend-proxy to `/grafana/`)
- **Default Credentials**: admin/admin
- **Data Source**: Prometheus
- **Dashboards**: Pre-configured for demo metrics

### OpenSearch Configuration
- **Container Image**: opensearchproject/opensearch
- **Port**: 9200
- **Purpose**: Stores OTLP logs from collector
- **Index Pattern**: `otel-logs-yyyy-MM-dd`

## Test Infrastructure

### Test Directory Structure
```
test/
├── README.md
└── tracetesting/
    ├── Dockerfile                  # Tracetest runner image
    ├── cli-config.yml              # CLI configuration
    ├── otelcol-config-tracetest.yml
    ├── tracetest-config.yaml       # Test environment config
    ├── tracetest-provision.yaml    # Pre-provisioning config
    ├── run.bash                    # Test orchestration script
    │
    ├── ad/
    │   └── [test definitions]      # Trace validation for ad service
    ├── cart/
    │   └── [test definitions]      # Cart service tests
    ├── checkout/
    │   └── [test definitions]      # Checkout flow tests
    ├── currency/
    │   └── [test definitions]      # Currency conversion tests
    ├── email/
    │   └── [test definitions]      # Email send tests
    ├── frontend/
    │   ├── e2e/                    # Playwright E2E tests
    │   ├── unit/                   # Jest unit tests
    │   └── [other]
    ├── payment/
    │   └── [test definitions]      # Payment processing tests
    ├── product-catalog/
    │   └── [test definitions]      # Catalog lookup tests
    ├── product-reviews/
    │   └── [test definitions]      # Review aggregation tests
    ├── recommendation/
    │   └── [test definitions]      # Recommendation tests
    └── shipping/
        └── [test definitions]      # Shipping service tests
```

### Test Compose File
- **Path**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/docker-compose-tests.yml`
- **Services**: Tracetest runner, test dependencies
- **Execution**: `make run-tests` or `make run-tracetesting`

## Build & Deployment Files

### Docker Images
- Each service has a `Dockerfile` in its directory
- Multi-stage builds common (builder + runtime stages)
- Base images: Alpine, official language runtimes, specialized containers
- Example: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/checkout/Dockerfile`

### Docker Compose Files
1. **Full Deployment**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/docker-compose.yml`
   - All 30 services
   - Complete observability stack
   - Resource limits per service
   - Logging configuration

2. **Minimal Deployment**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/docker-compose.minimal.yml`
   - Core services only (~15 services)
   - Reduced resource footprint
   - Same architecture, fewer features

3. **Test Environment**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/docker-compose-tests.yml`
   - Test-specific services
   - Test runners and dependencies

### Kubernetes Manifests
- **Main Manifest**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/kubernetes/opentelemetry-demo.yaml`
- **Generated From**: Helm chart (helm repo: open-telemetry/opentelemetry-demo)
- **Generation Command**: `make generate-kubernetes-manifests`
- **Namespace**: `otel-demo`
- **Resource Definitions**: Deployments, Services, ConfigMaps, PersistentVolumes

### Environment Configuration
- **Main**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/.env`
  - Service ports (AD_PORT, CART_PORT, etc.)
  - Database credentials
  - Image names and versions
  - OTEL exporter endpoints

- **Override**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/.env.override`
  - Production overrides
  - Security configurations

- **ARM64 Workaround**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/.env.arm64`
  - macOS M1/M2/M3/M4 Java fixes
  - Architecture-specific settings

## Build Tooling

### Makefile
- **Path**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/Makefile`
- **Key Targets**:
  - `all` - Run all checks
  - `build` - Build all service images
  - `start` - Start full demo
  - `start-minimal` - Start minimal demo
  - `stop` - Stop and remove containers
  - `restart` - Restart specific service
  - `redeploy` - Rebuild and restart service
  - `generate-protobuf` - Generate proto code
  - `run-tests` - Execute test suite
  - `check` - Lint and validation
  - `fix` - Auto-fix issues

### Code Generation
- **Proto Generator (IDE)**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/ide-gen-proto.sh`
- **Proto Generator (Docker)**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/docker-gen-proto.sh`
- **Sanitizer**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/internal/tools/sanitycheck.py`
- **Tools**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/internal/tools/tools.go`

### CI/CD
- **Workflows**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/.github/workflows/`
- **Integration Tests**: Run on PR and main
- **Image Publishing**: To ghcr.io/open-telemetry/demo:*

## Documentation Structure

### AI Knowledge Base
- **Path**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/docs/ai-knowledge/`
- **Sections**:
  - `architecture/` - System design (THIS DIRECTORY)
  - `communication/` - Service interaction patterns
  - `frontend/` - React UI architecture
  - `local-runbook/` - Setup instructions
  - `observability/` - OTel patterns and practices
  - `services/` - Individual service docs
  - `testing/` - Test strategies and execution
  - `ui-kit/` - Frontend component library

### Feature Documentation
- **Path**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/docs/features/`
- Documents feature behaviors and configurations

### Project-Level Documentation
- **Main README**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/README.md`
- **Contributing**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/CONTRIBUTING.md`
- **Changelog**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/CHANGELOG.md`
- **Project Rules**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/CLAUDE.md`

## Notable Patterns & Features

### Feature Flags (OpenFeature)
- **Provider**: flagd (launches as container)
- **Config**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/flagd/demo.flagd.json`
- **UI**: flagd-ui (Elixir Phoenix) on port 4000
- **Integration**: ad and cart services consume flags
- **URL**: `http://localhost:8080/feature/` (proxied)

### Kafka Messaging
- **Broker**: Kafka container on port 9092
- **Topics**: order_events (created by checkout)
- **Consumers**: accounting, fraud-detection
- **Pattern**: Async event distribution

### Database Persistence
- **PostgreSQL**: Stores accounting, product, user data
- **Valkey (Redis)**: In-memory cart cache
- **Data Initialization**: SQL scripts in service directories

### API Aggregation
- **Frontend** routes requests to multiple backend services
- **Pattern**: API composition via Express middleware
- **Services Called**: checkout, cart, product-catalog, recommendation, product-reviews

### AI/LLM Integration
- **Service**: llm (Python FastAPI)
- **Format**: OpenAI-compatible `/v1/chat/completions`
- **Use Case**: Product review summarization
- **Instrumentation**: opentelemetry-instrumentation-openai-v2
- **Span Attributes**: Gen AI specific (model, tokens, messages)

### Load Testing
- **Tool**: Locust (Python)
- **Location**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/load-generator/`
- **UI**: Web interface on port 8089, proxied to `/loadgen/`
- **Scenarios**: Realistic user journeys (browse, add-to-cart, checkout)

### Trace-Based Testing
- **Framework**: Tracetest
- **Assertions**: Validate trace spans match expected behavior
- **Coverage**: All major services
- **Execution**: `make run-tracetesting` with optional service filtering

### System Observability
- **Docker Metrics**: Container stats via collector
- **Host Metrics**: CPU, memory, disk, network via hostmetrics receiver
- **Database Metrics**: PostgreSQL query stats, table activity
- **Cache Metrics**: Valkey key counts, memory usage
- **Nginx Metrics**: HTTP request rates and latencies

## Service Port Mapping

```
Frontend/Web:
  frontend:3000 -> proxied to localhost:8080/
  load-generator:8089 -> proxied to localhost:8080/loadgen/
  jaeger:16686 -> proxied to localhost:8080/jaeger/ui/
  grafana:3000 -> proxied to localhost:8080/grafana/
  flagd-ui:4000 -> proxied to localhost:8080/feature/

gRPC Services:
  ad:8080 (java)
  cart:7070 (.NET)
  checkout:5050 (go)
  currency:50051 (c++)
  payment:8080 (node)
  product-catalog:3550 (go)
  product-reviews:8000 (python)
  recommendation:8000 (python)
  shipping:8080 (rust)

HTTP Services:
  email:8080 (ruby)
  llm:8000 (python)
  quote:8800 (php)
  image-provider:80 (nginx)
  otel-collector:4317 (grpc), 4318 (http)

Infrastructure:
  kafka:9092
  postgresql:5432
  opensearch:9200
  jaeger:16686, 4317
  prometheus:9090
  grafana:3000
```

## Uncertain/Complex Areas

1. **C++ Service Build Process**: Currency service compilation pipeline (compiler, linker, dependencies)
2. **Multi-Stage Docker Builds**: Some services use complex multi-stage Dockerfiles with conditional logic
3. **Kafka Topic Creation**: Automatic vs. manual topic provisioning (not fully documented)
4. **Feature Flag Evaluation**: Exact flagd protocol and caching behavior
5. **OTel Collector Sampling**: Whether sampling is configured anywhere (default unlimited)
6. **Load Generator Scenario Complexity**: Exact user journey simulation (checkout percentages, etc.)
7. **PostgreSQL Schema Initialization**: Table creation and seeding (init scripts location)
8. **OpenSearch Index Management**: Log retention policies, index rotation
9. **Kubernetes Resource Requests/Limits**: K8s manifest autoscaling policies
10. **Proto Compilation Order Dependencies**: Whether some services depend on others' proto generation

## Service Dependencies (Call Graph)

```
frontend (Next.js)
├── checkout (go)
│   ├── cart (.NET)
│   ├── currency (c++)
│   ├── payment (node)
│   ├── product-catalog (go)
│   ├── shipping (rust)
│   │   └── quote (php)
│   └── email (ruby)
├── product-catalog (go)
├── recommendation (python)
├── product-reviews (python)
│   └── llm (python)
│
frontend-proxy (envoy)
├── frontend (next.js)
├── load-generator (locust web ui)
├── jaeger ui
├── grafana
└── flagd-ui (elixir)

checkout (go)
└── kafka -> accounting (.NET), fraud-detection (java)

ad (java)
└── flagd (feature flag provider)

cart (.NET)
└── flagd (feature flag provider)

load-generator (python)
└── calls all public endpoints via frontend
```

---

**Last Updated**: May 27, 2026
**Source**: OpenTelemetry Community Demo (workshop fork)
**Total Services**: 30 (21 application + 6 infrastructure + 3 config/utility)
**Languages**: Go, Python, Java, .NET, Node.js, Rust, PHP, Ruby, C++, Elixir, React, React Native
