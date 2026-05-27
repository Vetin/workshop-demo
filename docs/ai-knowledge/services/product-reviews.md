# product-reviews

## Identity

- **Language**: Python
- **Framework**: gRPC Python + OpenAI client (for LLM calls)
- **Port**: 3551 (`PRODUCT_REVIEWS_PORT`)
- **Dockerfile**: `src/product-reviews/Dockerfile`
- **Main entry point**: `src/product-reviews/product_reviews_server.py`

## Responsibility

Stores and retrieves product reviews from PostgreSQL, computes average scores, and provides an AI assistant that answers questions about a product by calling an LLM. Exposes `ProductReviewService` gRPC methods.

## Dependencies

| Dependency | Protocol | Purpose |
|---|---|---|
| product-catalog | gRPC | Fetch product information for AI context |
| llm | HTTP (OpenAI API format) | AI assistant (`LLM_BASE_URL`) |
| postgresql | TCP/SQL (psycopg2) | Review storage |
| flagd | gRPC (OpenFeature) | Feature flags (`llmRateLimitError`) |
| otel-collector | OTLP gRPC | Telemetry export |

Environment variables: `PRODUCT_REVIEWS_PORT`, `DB_CONNECTION_STRING`, `LLM_BASE_URL`, `OPENAI_API_KEY`, `LLM_MODEL`, `LLM_HOST`, `LLM_PORT`, `PRODUCT_CATALOG_ADDR`, `FLAGD_HOST`, `FLAGD_PORT`.

## OTel Instrumentation

- **Approach**: `opentelemetry-instrument` binary (auto-instrumentation via `opentelemetry-bootstrap`) as the container entrypoint.
- **Manual spans**: `tracer.start_as_current_span()` used in `get_product_reviews`, `get_average_product_review_score`, `get_ai_assistant_response`.
- **GenAI**: `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true` — captures LLM prompt/response content in spans.
- **Log correlation**: `OTEL_PYTHON_LOG_CORRELATION=true`.
- **Exporter**: OTLP gRPC.

## gRPC Interface

Proto definition at `pb/demo.proto`:
```
service ProductReviewService {
  rpc GetProductReviews(GetProductReviewsRequest) returns (GetProductReviewsResponse){}
  rpc GetAverageProductReviewScore(...) returns (...){}
  rpc AskProductAIAssistant(AskProductAIAssistantRequest) returns (AskProductAIAssistantResponse){}
}
```
Callers: frontend (`src/frontend/gateways/rpc/ProductReview.gateway.ts`).

## LLM Tool Use

`product_reviews_server.py` defines two tools for the OpenAI function-calling API:
- `fetch_product_reviews` — executes SQL query against PostgreSQL
- `fetch_product_info` — calls product-catalog gRPC

The `llmRateLimitError` feature flag causes 50% of AI assistant calls to use `astronomy-llm-rate-limit` model against the mock LLM, which returns a 429, demonstrating error handling.

## Key Source Files

- `src/product-reviews/product_reviews_server.py` — gRPC server + LLM orchestration
- `src/product-reviews/database.py` — PostgreSQL access functions
- `src/product-reviews/metrics.py` — OTel metrics setup
- `src/product-reviews/demo_pb2*.py` — generated protobuf stubs
- `src/product-reviews/Dockerfile`

## Risky Notes

1. The LLM call is plain HTTP using the OpenAI client — no gRPC contract. If `LLM_BASE_URL` or `LLM_PORT` changes, the service fails at runtime with an HTTP error, not a startup error.
2. `OPENAI_API_KEY` is required by the OpenAI client even when using the mock LLM. It defaults to a dummy value but must not be empty.
