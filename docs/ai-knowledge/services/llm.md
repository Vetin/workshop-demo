# llm

## Identity

- **Language**: Python
- **Framework**: Flask
- **Port**: 8000 (`LLM_PORT`)
- **Dockerfile**: `src/llm/Dockerfile`
- **Main entry point**: `src/llm/app.py`

## Responsibility

Mock LLM service that serves pre-generated product review summaries via an OpenAI-compatible HTTP API. Used by product-reviews as the AI backend when no real OpenAI API key is provided. Also implements a simulated rate-limit error path for the `llmRateLimitError` feature flag scenario.

## Dependencies

| Dependency | Protocol | Purpose |
|---|---|---|
| flagd | gRPC (OpenFeature) | Feature flag (`inaccurateLLM` scenario) |

Environment variables: `FLAGD_HOST`, `FLAGD_PORT`, `LLM_PORT`.

## OTel Instrumentation

- **None**. The llm service has no `OTEL_*` environment variables in docker-compose. It is intentionally uninstrumented to serve as a contrast example.

## HTTP Interface

Serves an OpenAI-compatible API at `http://llm:8000/v1/...`. product-reviews connects via `LLM_BASE_URL=http://${LLM_HOST}:${LLM_PORT}/v1`.

Two data files mounted at runtime:
- `src/llm/product-review-summaries/product-review-summaries.json` — accurate summaries
- `src/llm/product-review-summaries/inaccurate-product-review-summaries.json` — inaccurate summaries (used when `inaccurateLLM` flag is enabled)

## Key Source Files

- `src/llm/app.py` — Flask app with OpenAI-compatible routes
- `src/llm/product-review-summaries/product-review-summaries.json` — pre-generated review data
- `src/llm/product-review-summaries/inaccurate-product-review-summaries.json`
- `src/llm/Dockerfile`

## Risky Notes

This service has no OTel instrumentation. Traces from product-reviews that call the LLM will have no corresponding child spans from the LLM side — the call appears as a gap in distributed traces.
