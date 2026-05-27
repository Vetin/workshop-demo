# Python Language Knowledge

Services:
- `src/llm/` — LLM proxy (Flask)
- `src/load-generator/` — Locust + Playwright load generator
- `src/product-reviews/` — gRPC service, OpenAI client
- `src/recommendation/` — gRPC recommendation service

## Version and Toolchain

- Python 3.11+
- Dependencies managed via `requirements.txt` or `pyproject.toml` per service

## Commands

| Task | Command | Working Directory |
|---|---|---|
| Install deps | `pip install -r requirements.txt` or `pip install .` | service directory |
| Test | `pytest` | service directory (if tests exist) |
| Lint | `flake8 .` or `ruff check .` | service directory |
| Format | `black .` or `ruff format .` | service directory |

## OpenTelemetry Instrumentation — Per Service

### llm (`src/llm/`)

No OTel instrumentation. This service is intentionally un-instrumented as
a teaching example; do not add OTel unless the spec explicitly requires it.

### load-generator (`src/load-generator/`)

Manual Python SDK with OTLP gRPC exporter:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
```

Traces are emitted to represent synthetic user journeys. Existing span names
and attributes are used by Tracetest — do not rename them without updating
`test/tracetesting/`.

### product-reviews (`src/product-reviews/`)

Hybrid approach: `opentelemetry-instrument` auto-instrumentation wraps the
service entry point, plus manual spans for LLM/GenAI capture:

```python
with tracer.start_as_current_span("generate_review") as span:
    span.set_attribute("gen_ai.system", "openai")
    span.set_attribute("gen_ai.request.model", model)
    # ...
    span.record_exception(exc)
```

PII rule: never add order details, customer names, or email addresses to span
attributes in this service — LLM calls are visible in traces.

### recommendation (`src/recommendation/`)

Auto-instrumentation via `opentelemetry-bootstrap` + `opentelemetry-instrument`
at container ENTRYPOINT. No manual span creation currently.

## Generated Proto Stubs

| Service | Generated Files |
|---|---|
| recommendation | `src/recommendation/demo_pb2.py`, `src/recommendation/demo_pb2_grpc.py` |
| product-reviews | `src/product-reviews/demo_pb2.py`, `src/product-reviews/demo_pb2_grpc.py` |

**Do not hand-edit these files.** Regenerate with:

```
make docker-generate-protobuf
```

## Key Python Idioms

- Add type hints to all public functions:
  ```python
  def get_product(product_id: str) -> Product: ...
  ```
- Use context managers for resources and spans:
  ```python
  with tracer.start_as_current_span("span_name") as span:
      ...
  ```
- Record exceptions before re-raising:
  ```python
  except Exception as e:
      span.record_exception(e)
      span.set_status(StatusCode.ERROR, str(e))
      raise
  ```
- Use `logging` module, not `print`, for diagnostics.

## Common Failure Modes

| Symptom | Root Cause |
|---|---|
| Auto-instrumentation not active | `opentelemetry-instrument` not first token in Dockerfile `ENTRYPOINT` |
| Double-instrumentation errors at startup | Both auto and manual init in same process |
| Import error for `demo_pb2` | Stale generated stubs after `pb/demo.proto` change — regenerate |
| gRPC channel hangs | Missing `OTEL_EXPORTER_OTLP_ENDPOINT` or collector not reachable |
| PII leak in traces | span attribute set from `request.body` or order data in product-reviews |

## PII Risk — product-reviews

product-reviews calls an external LLM (OpenAI). Treat all LLM prompt content
and completion text as potentially sensitive. Specifically:

- Do not set `gen_ai.prompt` or similar attributes with full request bodies.
- Do not attach order ID, user ID, or email as span attributes.
- Safe attributes: `gen_ai.system`, `gen_ai.request.model`, latency, token counts.

## Implementer Rules

1. Keep `opentelemetry-instrument` as the first command in Dockerfile `ENTRYPOINT`
   for recommendation and product-reviews.
2. Do not re-initialize `TracerProvider` inside a request handler.
3. Never hand-edit `demo_pb2*.py` — regenerate from proto.
4. In product-reviews, follow the PII rule above for all new span attributes.

## Reviewer Checks

- `opentelemetry-instrument` missing or not first in ENTRYPOINT.
- Manual `TracerProvider` init present alongside auto-instrumentation
  (causes double-export).
- `demo_pb2.py` modified by hand.
- PII (email, name, order content) added to span attributes in product-reviews.
- `span.record_exception` missing in except blocks that catch and re-raise.
- `context.TODO()` equivalent: bare `context_api.get_current()` called without
  propagating context from gRPC servicer.
