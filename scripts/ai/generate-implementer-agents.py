#!/usr/bin/env python3
"""
generate-implementer-agents.py

Reference implementation: groups services from service-inventory.json by
language and generates one implementer agent file per group.

Language → agent name mapping:
  C#          → csharp-dotnet-implementer
  Go          → go-implementer
  Java        → java-implementer
  Kotlin      → kotlin-implementer
  Python      → python-implementer
  TypeScript  → typescript-frontend-implementer
  Ruby        → ruby-implementer
  Rust        → rust-implementer
  PHP         → php-implementer
  Elixir      → elixir-implementer
  JavaScript  → javascript-node-implementer
  N/A         → infra-otel-implementer  (infrastructure services)

Run from repo root:
    python scripts/ai/generate-implementer-agents.py
    python scripts/ai/generate-implementer-agents.py --force
"""

import json
import pathlib
import argparse
import sys
from collections import defaultdict

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
INVENTORY_PATH = REPO_ROOT / "docs/ai-knowledge/services/service-inventory.json"
AGENTS_DIR = REPO_ROOT / ".claude/agents"

# ---------------------------------------------------------------------------
# Language → implementer name mapping
# ---------------------------------------------------------------------------
LANGUAGE_TO_AGENT: dict[str, str] = {
    "C#":         "csharp-dotnet",
    "Go":         "go",
    "Java":       "java",
    "Kotlin":     "kotlin",
    "Python":     "python",
    "TypeScript": "typescript-frontend",
    "Ruby":       "ruby",
    "Rust":       "rust",
    "PHP":        "php",
    "Elixir":     "elixir",
    "JavaScript": "javascript-node",
    "N/A":        "infra-otel",
    # Catch-all for any C++ or other languages that appear in future inventory entries
    "C++":        "cpp",
}

# ---------------------------------------------------------------------------
# Per-language OTel instrumentation guidance embedded in agent files
# ---------------------------------------------------------------------------
OTEL_GUIDANCE: dict[str, str] = {
    "C#": """\
## OTel Instrumentation Patterns (C# / .NET)

```csharp
// Manual span
using System.Diagnostics;
private static readonly ActivitySource Source = new("MyService");
using var activity = Source.StartActivity("OperationName");
activity?.SetTag("key", "value");
activity?.SetStatus(ActivityStatusCode.Error, "description");

// Metrics
private static readonly Meter Meter = new("MyService");
private static readonly Counter<long> Requests = Meter.CreateCounter<long>("requests.total");
```

- Wire up via `builder.Services.AddOpenTelemetry().WithTracing(...).WithMetrics(...)`.
- Preserve `instrument.sh` for services (like accounting) that use auto-instrumentation bootstrap.
- Never hardcode `OTEL_SERVICE_NAME` or `OTEL_EXPORTER_OTLP_ENDPOINT`; they come from env vars.
""",
    "Go": """\
## OTel Instrumentation Patterns (Go)

```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
)

tracer := otel.Tracer("my-service")
ctx, span := tracer.Start(ctx, "OperationName")
defer span.End()
span.SetAttributes(attribute.String("key", "value"))
```

- Use `otelgrpc` interceptors for gRPC, `otelhttp` for HTTP.
- Bridge `slog` via `otelslog` for structured logs.
- Exporter: OTLP gRPC (`go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc`).
""",
    "Java": """\
## OTel Instrumentation Patterns (Java)

- Services use the OpenTelemetry Java agent (`JAVA_TOOL_OPTIONS=-javaagent:/path/to/agent.jar`).
- Manual API for custom spans:

```java
Tracer tracer = GlobalOpenTelemetry.getTracer("my-service");
Span span = tracer.spanBuilder("OperationName").startSpan();
try (Scope scope = span.makeCurrent()) {
    span.setAttribute("key", "value");
} finally {
    span.end();
}
```

- Do not remove or override the `JAVA_TOOL_OPTIONS` env var.
""",
    "Kotlin": """\
## OTel Instrumentation Patterns (Kotlin)

- fraud-detection uses the OpenTelemetry Java agent (same JVM, `JAVA_TOOL_OPTIONS`).
- Kafka consumer spans are emitted automatically; enable experimental span attributes via
  `OTEL_INSTRUMENTATION_KAFKA_EXPERIMENTAL_SPAN_ATTRIBUTES=true`.
- Manual spans use the same OpenTelemetry Java API as the Java services.
""",
    "Python": """\
## OTel Instrumentation Patterns (Python)

```python
from opentelemetry import trace

tracer = trace.get_tracer("my-service")
with tracer.start_as_current_span("OperationName") as span:
    span.set_attribute("key", "value")
```

- Services use `opentelemetry-instrument` (auto-instrumentation) or manual SDK setup.
- Exporter: OTLP gRPC (`opentelemetry-exporter-otlp-proto-grpc`).
- For GenAI / LLM services, enable GenAI capture via `OTEL_PYTHON_LOG_CORRELATION=true`.
""",
    "TypeScript": """\
## OTel Instrumentation Patterns (TypeScript / Node.js)

```typescript
import { trace } from '@opentelemetry/api';

const tracer = trace.getTracer('my-service');
const span = tracer.startSpan('OperationName');
span.setAttribute('key', 'value');
span.end();
```

- Server-side: `@opentelemetry/auto-instrumentations-node` with OTLP gRPC exporter.
- Browser-side: OTLP HTTP trace export via `PUBLIC_OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`.
- Do not remove the browser instrumentation initializer in `src/frontend/utils/telemetry/`.
""",
    "Ruby": """\
## OTel Instrumentation Patterns (Ruby)

```ruby
OpenTelemetry::SDK.configure do |c|
  c.use_all  # auto-instrumentation
end

tracer = OpenTelemetry.tracer_provider.tracer('my-service')
tracer.in_span('OperationName') do |span|
  span.set_attribute('key', 'value')
end
```

- Auto-instrumentation for Sinatra via `opentelemetry-instrumentation-sinatra`.
- Exporter: OTLP HTTP (`opentelemetry-exporter-otlp`).
""",
    "Rust": """\
## OTel Instrumentation Patterns (Rust)

```rust
use opentelemetry::global;
use opentelemetry_sdk::trace as sdktrace;

let tracer = global::tracer("my-service");
let span = tracer.start("OperationName");
let _guard = mark_span_as_active(span);
```

- Uses `opentelemetry-instrumentation-actix-web` (`RequestTracing`, `RequestMetrics` middleware).
- Exporter: OTLP gRPC.
- Preserve middleware registrations in `src/shipping/src/main.rs`.
""",
    "PHP": """\
## OTel Instrumentation Patterns (PHP)

```php
$tracer = Globals::tracerProvider()->getTracer('my-service');
$span = $tracer->spanBuilder('OperationName')->startSpan();
$scope = $span->activate();
// ... work ...
$span->end();
$scope->detach();
```

- Auto-load: `OTEL_PHP_AUTOLOAD_ENABLED=true` via Composer autoload hook.
- Exporter: OTLP HTTP.
""",
    "Elixir": """\
## OTel Instrumentation Patterns (Elixir)

```elixir
require OpenTelemetry.Tracer

OpenTelemetry.Tracer.with_span "operation_name" do
  OpenTelemetry.Span.set_attribute("key", "value")
end
```

- Uses `opentelemetry_exporter` library.
- Exporter: OTLP HTTP.
""",
    "JavaScript": """\
## OTel Instrumentation Patterns (JavaScript / Node.js)

```javascript
const { trace } = require('@opentelemetry/api');

const tracer = trace.getTracer('my-service');
const span = tracer.startSpan('OperationName');
span.setAttribute('key', 'value');
span.end();
```

- Auto-instrumentation via `@opentelemetry/auto-instrumentations-node` in `opentelemetry.js`.
- Exporter: OTLP gRPC.
""",
    "N/A": """\
## Infrastructure Services — OTel Notes

- These services expose metrics/traces natively or via the OpenTelemetry Collector.
- The Collector (`src/otel-collector/otelcol-config.yml`) is the central hub: do not change
  receiver or exporter configuration without understanding the downstream effects on Jaeger,
  Prometheus, and OpenSearch.
- Envoy (frontend-proxy) and nginx (image-provider) use native OTel modules; preserve the
  tracing stanzas in their config templates.
- flagd OTel support is configured via `FLAGD_METRICS_EXPORTER=otel`; do not disable.
""",
    "C++": """\
## OTel Instrumentation Patterns (C++)

```cpp
auto tracer = opentelemetry::trace::Provider::GetTracerProvider()->GetTracer("my-service");
auto span = tracer->StartSpan("OperationName");
span->SetAttribute("key", opentelemetry::common::AttributeValue("value"));
span->End();
```

- Uses the OpenTelemetry C++ SDK (manual).
- Exporter: OTLP gRPC.
""",
}

# ---------------------------------------------------------------------------
# Build rules per agent type
# ---------------------------------------------------------------------------
def build_rules(lang: str, services: list[dict]) -> str:
    """Return a numbered rules block appropriate for the language group."""
    service_dirs = " or ".join(f"`src/{s['name']}/`" for s in services)

    build_hint = {
        "C#": "dotnet build / dotnet test",
        "Go": "go build ./... / go test ./...",
        "Java": "gradle build (from service root)",
        "Kotlin": "gradle build (from service root)",
        "Python": "python -m pytest (where tests exist)",
        "TypeScript": "npm run build / npm test",
        "Ruby": "bundle exec ruby -e 'require_relative \"email_server\"'",
        "Rust": "cargo build / cargo test",
        "PHP": "composer install / php -l",
        "Elixir": "mix compile / mix test",
        "JavaScript": "npm run build / npm test",
        "N/A": "validate config YAML / run integration smoke test",
        "C++": "cmake --build / ctest",
    }.get(lang, "run the service's build tool")

    return f"""\
## Rules

1. **Preserve all OTel instrumentation.** Never remove, comment out, or bypass tracer/meter
   setup, exporter registrations, or auto-instrumentation bootstrap scripts.
2. **Never hide telemetry-impacting changes.** If your change affects what spans, metrics,
   or logs are emitted, state this explicitly in your output.
3. **Cite every changed file** in your output (absolute path from repo root).
4. **Run build/lint after changes:** `{build_hint}` in {service_dirs}.
5. **Do not modify generated protobuf files** (`.proto`-derived sources) unless you also
   update the generator path and document it.
6. **Read the service knowledge file first** before editing any service (see Owned Services).
"""


def render_implementer(agent_slug: str, lang: str, services: list[dict]) -> str:
    """Return the full Markdown content for an implementer agent."""
    agent_name = f"{agent_slug}-implementer"

    # Human-readable title
    lang_label = lang if lang != "N/A" else "Infrastructure (N/A)"
    description = (
        f"Edit-capable implementer for {lang_label} services in the OpenTelemetry Demo. "
        f"Use for feature work, bug fixes, and instrumentation changes in: "
        + ", ".join(s["name"] for s in services)
        + "."
    )

    # Owned services section
    owned_lines = []
    for s in services:
        owned_lines.append(f"- **{s['name']}** — `src/{s['name']}/`")
    owned_md = "\n".join(owned_lines)

    # Knowledge files
    knowledge_lines = [f"- `docs/ai-knowledge/services/{s['name']}.md`" for s in services]
    knowledge_md = "\n".join(knowledge_lines)

    # Key files table
    table_rows = []
    for s in services:
        ep = s.get("entrypoint") or "n/a"
        table_rows.append(f"| {s['name']} | `{ep}` | entry point |")
        if s.get("dockerfile"):
            table_rows.append(f"| {s['name']} | `{s['dockerfile']}` | Dockerfile |")
    table_md = (
        "| Service | File | Purpose |\n"
        "|---------|------|---------|\n"
        + "\n".join(table_rows)
    )

    otel_block = OTEL_GUIDANCE.get(lang, "")
    rules_block = build_rules(lang, services)

    return f"""\
---
name: {agent_name}
description: {description}
tools: Read, Edit, Write, Bash, Grep, Glob
model: sonnet
---

## Owned Services

{owned_md}

## Before Editing Any Service

Always read the service knowledge file first:

{knowledge_md}

These files contain authoritative information about service behavior, dependencies, and
instrumentation contracts. Do not rely on assumptions.

## Key Files

{table_md}

{otel_block}
{rules_block}
"""


def group_services_by_language(services: list[dict]) -> dict[str, list[dict]]:
    """Return a dict mapping agent-slug → list of services."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for svc in services:
        lang = svc.get("language", "N/A")
        slug = LANGUAGE_TO_AGENT.get(lang, lang.lower().replace(" ", "-").replace("/", "-"))
        groups[slug].append(svc)
    return dict(groups)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate implementer agent files grouped by language from service-inventory.json"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing agent files",
    )
    args = parser.parse_args()

    if not INVENTORY_PATH.exists():
        print(f"ERROR: inventory not found at {INVENTORY_PATH}", file=sys.stderr)
        sys.exit(1)

    with INVENTORY_PATH.open() as f:
        services = json.load(f)

    AGENTS_DIR.mkdir(parents=True, exist_ok=True)

    groups = group_services_by_language(services)

    # Resolve the original language for each group (needed for otel guidance lookup)
    slug_to_lang: dict[str, str] = {}
    for svc in services:
        lang = svc.get("language", "N/A")
        slug = LANGUAGE_TO_AGENT.get(lang, lang.lower().replace(" ", "-").replace("/", "-"))
        slug_to_lang[slug] = lang  # last one wins, but all in the group share the same lang

    generated = 0
    skipped = 0

    for slug, group_services in sorted(groups.items()):
        out_path = AGENTS_DIR / f"{slug}-implementer.md"
        lang = slug_to_lang.get(slug, "N/A")

        if out_path.exists() and not args.force:
            print(
                f"  skip  {out_path.relative_to(REPO_ROOT)}"
                f"  (exists; use --force to overwrite)"
            )
            skipped += 1
            continue

        content = render_implementer(slug, lang, group_services)
        out_path.write_text(content, encoding="utf-8")
        svc_names = ", ".join(s["name"] for s in group_services)
        print(f"  write  {out_path.relative_to(REPO_ROOT)}  [{svc_names}]")
        generated += 1

    print(f"\nDone. Generated: {generated}  Skipped: {skipped}")


if __name__ == "__main__":
    main()
