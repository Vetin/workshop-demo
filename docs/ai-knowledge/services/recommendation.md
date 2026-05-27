# recommendation

## Identity

- **Language**: Python
- **Framework**: gRPC Python
- **Port**: 9001 (`RECOMMENDATION_PORT`)
- **Dockerfile**: `src/recommendation/Dockerfile`
- **Main entry point**: `src/recommendation/recommendation_server.py`

## Responsibility

Returns a list of recommended product IDs, excluding products the user is already viewing. Supports a `recommendationCacheFailure` feature flag that simulates a memory-leak scenario by growing a cached product list indefinitely.

## Dependencies

| Dependency | Protocol | Purpose |
|---|---|---|
| product-catalog | gRPC | Fetch all products for recommendation pool |
| flagd | gRPC (OpenFeature) | Feature flag `recommendationCacheFailure` |
| otel-collector | OTLP gRPC | Telemetry export |

Environment variables: `RECOMMENDATION_PORT`, `PRODUCT_CATALOG_ADDR`, `FLAGD_HOST`, `FLAGD_PORT`.

## OTel Instrumentation

- **Approach**: `opentelemetry-instrument` binary (auto-instrumentation) as entrypoint: `ENTRYPOINT ["/venv/bin/opentelemetry-instrument", "/venv/bin/python", "recommendation_server.py"]`.
- `opentelemetry-bootstrap -a install` during Docker build auto-discovers and installs instrumentors for all installed packages.
- **Manual spans**: `tracer.start_as_current_span("get_product_list")` in recommendation_server.py.
- **Log correlation**: `OTEL_PYTHON_LOG_CORRELATION=true`.
- **OTLP gRPC**: `OTLPLogExporter(insecure=True)`.

## gRPC Interface

Proto definition at `pb/demo.proto`:
```
service RecommendationService {
  rpc ListRecommendations(ListRecommendationsRequest) returns (ListRecommendationsResponse){}
}
```
Callers: frontend (`src/frontend/gateways/rpc/Recommendations.gateway.ts`).

## Feature Flag Behavior

`recommendationCacheFailure` (recommendation_server.py line 78):
- When enabled, 50% of requests fetch from product-catalog and append to `cached_ids` plus 25% extra, never trimming the list.
- This simulates a cache-leak memory problem visible in memory metrics.

## Key Source Files

- `src/recommendation/recommendation_server.py` — gRPC server + feature-flag cache logic
- `src/recommendation/metrics.py` — OTel metrics initialization
- `src/recommendation/demo_pb2*.py` — generated protobuf stubs
- `src/recommendation/Dockerfile`

## Risky Notes

The docker-compose memory limit is set to 500M (`# This is high to enable supporting the recommendationCache feature flag use case`). Reducing it will cause OOM when `recommendationCacheFailure` is active.
