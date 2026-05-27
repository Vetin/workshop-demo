# OpenTelemetry Demo Architecture - Overview

## What is the OpenTelemetry Demo?

The OpenTelemetry Demo (Astronomy Shop) is a distributed systems teaching application that demonstrates observability patterns and OpenTelemetry instrumentation across multiple services. It simulates a real-world e-commerce microservice platform with realistic patterns: asynchronous messaging, RPC communication, database operations, feature flags, and a complete observability stack.

**Purpose**: Serve as a reference implementation for OpenTelemetry instrumentation across multiple languages and frameworks, demonstrating traces, metrics, logs, and generated AI summaries of product reviews.

**Key Teaching Goals**:
- Show how to instrument diverse technology stacks with OpenTelemetry
- Demonstrate distributed tracing across service boundaries
- Illustrate metrics collection and analysis
- Model realistic inter-service communication patterns
- Showcase feature flags in production systems
- Demonstrate AI/LLM integration observability

## Repository Location

**Workspace**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo`

**Key Files**:
- `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/Makefile` - Build/deployment commands
- `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/docker-compose.yml` - Docker Compose deployment (full)
- `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/docker-compose.minimal.yml` - Docker Compose deployment (minimal)
- `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/kubernetes/opentelemetry-demo.yaml` - Kubernetes manifest
- `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/.env` - Environment configuration
- `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/pb/demo.proto` - gRPC service contracts

## Service Inventory

Total services: 30 (21 application services + 6 infrastructure services + 3 utility services)

### Application Services (Core Demo)

| Service | Language | Framework | Purpose |
|---------|----------|-----------|---------|
| **checkout** | Go | gRPC | Orchestrates checkout process; calls cart, currency, email, payment, product-catalog, shipping services |
| **cart** | .NET/C# | ASP.NET Core | Stores user shopping carts in Valkey; integrates with checkout flow |
| **payment** | Node.js | Express | Validates and processes payments; called by checkout service |
| **product-catalog** | Go | gRPC | Provides product database and availability; consulted during checkout |
| **shipping** | Rust | Actix-web | Manages shipment tracking; queries quote service for pricing |
| **quote** | PHP | Custom HTTP | Calculates shipping costs based on item count; queries database |
| **currency** | C++ | gRPC | Converts prices between currencies via exchange rate lookups |
| **ad** | Java (Gradle) | Spring Boot | Returns contextual advertisements; integrates with feature flags |
| **recommendation** | Python | FastAPI/gRPC | Generates product recommendations; processes via queue |
| **product-reviews** | Python | FastAPI/gRPC | Returns product reviews with AI-generated summaries via LLM service |
| **llm** | Python | FastAPI | Mock LLM service following OpenAI API format; generates review summaries |
| **email** | Ruby | Custom | Simulates email sending; receives order details from checkout |
| **accounting** | .NET/C# | ASP.NET Core | Consumes order events from Kafka; records transactions in PostgreSQL |
| **fraud-detection** | Java (Gradle) | Spring Boot | Consumes order events from Kafka; identifies suspicious transactions |
| **load-generator** | Python | Locust | Creates synthetic traffic to simulate real user behavior; web UI at `/loadgen/` |

### Frontend & Gateway Services

| Service | Language | Framework | Purpose |
|---------|----------|-----------|---------|
| **frontend** | React | Next.js 14 | E-commerce web UI; client-side React + Next.js API routes for backend integration |
| **frontend-proxy** | Envoy | Envoy Configuration | Reverse proxy routing for web interfaces (Jaeger, Grafana, frontend, load-gen) |
| **flagd-ui** | Elixir | Phoenix | Web UI for managing feature flags (OpenFeature spec compliance) |
| **flagd** | Configuration | JSON | Feature flag store and provider (no service code, just config file) |
| **react-native-app** | React Native | TypeScript | Example mobile app for iOS/Android |

### Infrastructure & Observability Services

| Service | Purpose | Configuration |
|---------|---------|----------------|
| **otel-collector** | OpenTelemetry Collector | Receives traces/metrics/logs; exports to Jaeger/Prometheus/OpenSearch |
| **jaeger** | Distributed Tracing Backend | Stores and queries trace data; UI at `http://localhost:8080/jaeger/ui/` |
| **prometheus** | Metrics Database | Time-series metric storage; Prometheus server |
| **grafana** | Metrics Visualization | Dashboards and alerting; UI at `http://localhost:8080/grafana/` |
| **opensearch** | Log Storage | Stores structured logs received via OTLP from collector |
| **postgresql** | Relational Database | Stores accounting records, product catalog, user accounts |
| **kafka** | Message Queue | Asynchronous order events for accounting and fraud-detection services |
| **image-provider** | Static Content Server | Nginx with OTel instrumentation; serves product images |

## Deployment Topology

### Docker Compose (Default)
- **File**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/docker-compose.yml`
- **Command**: `make start` or `docker compose up`
- **URL**: `http://localhost:8080` (frontend)
- **Components**: All 30 services
- **Network**: Bridge network named `opentelemetry-demo`

### Docker Compose (Minimal)
- **File**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/docker-compose.minimal.yml`
- **Command**: `make start-minimal`
- **Purpose**: Reduced footprint for development; excludes optional services
- **Includes**: Core services + Jaeger/Prometheus/Grafana, excludes some features like load-gen UI

### Kubernetes
- **File**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/kubernetes/opentelemetry-demo.yaml`
- **Type**: Helm-generated manifest
- **Namespace**: `otel-demo`
- **Command**: `make generate-kubernetes-manifests` (regenerates from Helm)

## Service Communication Patterns

### gRPC Services
- **checkout** <-> **cart**, **currency**, **product-catalog**, **shipping**, **quote**
- **recommendation** <-> (asynchronous queue-based)
- **product-reviews** <-> **llm** (mock LLM)
- Protocol files generated from `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/pb/demo.proto`

### REST/HTTP Services
- **frontend** -> checkout, cart, product-catalog, recommendation, product-reviews (via Next.js API routes)
- **email** receives JSON via HTTP
- **quote** HTTP endpoints
- **llm** exposes OpenAI-compatible `/v1/chat/completions` endpoint

### Asynchronous Messaging
- **checkout** -> Kafka (order_events topic)
- **accounting** consumes order_events
- **fraud-detection** consumes order_events

### Feature Flags
- **flagd** JSON config at `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/flagd/demo.flagd.json`
- **flagd-ui** Phoenix app for editing flags
- **ad** service integrates with flagd for A/B testing
- **cart** integrates with flagd for feature control

## Observability Stack

### Tracing
- **Collector**: OpenTelemetry Collector at `http://otel-collector:4317` (gRPC) / `http://otel-collector:4318` (HTTP)
- **Backend**: Jaeger at `http://jaeger:16686` (UI) / `http://jaeger:4317` (OTLP receiver)
- **Configuration**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/src/otel-collector/otelcol-config.yml`

### Metrics
- **Sources**: Application metrics (spans, custom metrics) + system metrics (CPU, memory, disk)
- **Collector**: OpenTelemetry Collector -> Prometheus exporter
- **Storage**: Prometheus at `http://prometheus:9090`
- **Visualization**: Grafana at `http://localhost:8080/grafana/` (admin/admin)

### Logs
- **Receiver**: OpenTelemetry Collector OTLP endpoint
- **Storage**: OpenSearch at `http://opensearch:9200`
- **Format**: Structured OTLP logs

### Special Metrics
- **spanmetrics connector**: Converts traces to metrics (latency histograms, throughput)
- **Docker stats**: Container CPU/memory
- **PostgreSQL metrics**: Query performance, table stats
- **Redis (Valkey) metrics**: Cache hit rates, memory usage
- **Image provider (Nginx) metrics**: HTTP request rates and latencies

## Environment Configuration

- **Main config**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/.env`
- **Override config**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/.env.override`
- **ARM64 (macOS) config**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/.env.arm64`

Key variables: `DEMO_VERSION`, `IMAGE_NAME`, `OTEL_EXPORTER_OTLP_ENDPOINT`, service ports

## Testing & Validation

### Test Types
- **Integration Tests**: Tracetest-based trace validation (`/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/test/tracetesting/`)
- **Frontend Tests**: Node.js/Playwright tests for React app
- **Test Compose**: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/docker-compose-tests.yml`

### Test Execution
- Command: `make run-tests`
- Trace testing: `make run-tracetesting`

## Generated Code

Proto files generate code in:
- **Go**: `/src/checkout/genproto/oteldemo/`, `/src/product-catalog/genproto/oteldemo/`
- **Python**: `/src/recommendation/demo_pb2.py`, `/src/product-reviews/demo_pb2.py`
- **TypeScript**: `/src/frontend/protos/demo.ts`

Generation:
- **Command**: `make generate-protobuf` (IDE) or `make docker-generate-protobuf` (Docker)
- **Scripts**: `ide-gen-proto.sh`, `docker-gen-proto.sh`

## Build & Run Commands

| Task | Command |
|------|---------|
| Start demo | `make start` |
| Stop demo | `make stop` |
| Restart service | `make restart service=checkout` |
| Rebuild service | `make redeploy service=checkout` |
| Build all images | `make build` |
| Generate protos | `make generate-protobuf` |
| Run tests | `make run-tests` |
| Access frontend | `http://localhost:8080/` |
| Access Jaeger | `http://localhost:8080/jaeger/ui/` |
| Access Grafana | `http://localhost:8080/grafana/` |
| Access load-gen | `http://localhost:8080/loadgen/` |
| Access feature flags | `http://localhost:8080/feature/` |

## Key Framework Versions

- **Go**: 1.22+
- **Java**: JDK 21+ (with Gradle)
- **Python**: 3.11+
- **.NET**: 8.0+
- **Node.js**: 20+
- **Rust**: Latest stable
- **PHP**: 8.1+
- **Ruby**: 3.4+
- **Elixir**: 1.14+ with Phoenix 1.7+
- **C++**: Standard library features

## Architecture Patterns Demonstrated

1. **Polyglot Microservices**: Go, Python, Java, .NET, Node.js, Rust, PHP, Ruby, Elixir, C++
2. **Distributed Tracing**: OpenTelemetry instrumentation across all services
3. **Asynchronous Patterns**: Kafka-based event streaming (orders)
4. **Caching**: Valkey/Redis for cart data
5. **Database Patterns**: PostgreSQL for transactional data
6. **Feature Flags**: OpenFeature spec with flagd
7. **API Composition**: Frontend aggregates multiple backend services
8. **AI Integration**: Mock LLM with observability instrumentation
9. **Load Testing**: Locust-based synthetic traffic generation
10. **Observability**: Complete OTel stack (traces, metrics, logs)

## Special Capabilities

- **AI Span Attributes**: opentelemetry-instrumentation-openai-v2 for generative AI monitoring
- **HTTP Check Metrics**: Frontend proxy availability monitoring
- **System Metrics**: Host CPU, memory, disk via collector scrapers
- **Database Observability**: PostgreSQL and Valkey metrics via collector receivers
- **Container Metrics**: Docker stats via collector
- **NextJS Auto-instrumentation**: Frontend traces gRPC and REST calls
- **Load Patterns**: Realistic user journey simulation via Locust

---

**Last Updated**: May 27, 2026
**Source**: OpenTelemetry Community Demo (workshop fork)
