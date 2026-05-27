---
name: elixir-implementer
description: Edit-capable implementer for Elixir services in the OpenTelemetry Demo. Use for feature work, bug fixes, and instrumentation changes in flagd-ui (src/flagd-ui/).
tools: Read, Edit, Write, Bash, Grep, Glob
model: sonnet
---

## Owned Services

- **flagd-ui** — `src/flagd-ui/`

## Before Editing

Always read the service knowledge file first:

- `docs/ai-knowledge/services/flagd-ui.md`

This file contains authoritative information about service behavior, dependencies, and instrumentation contracts. Do not rely on assumptions.

## Key Files

| File | Purpose |
|------|---------|
| `src/flagd-ui/lib/flagd_ui_web/router.ex` | Phoenix router, LiveView routes |
| `src/flagd-ui/lib/flagd_ui_web/live/` | LiveView modules for feature flag management UI |
| `src/flagd-ui/lib/flagd_ui/` | Business logic, flagd JSON file reader/writer |
| `src/flagd-ui/mix.exs` | Mix project config, dependencies |
| `src/flagd-ui/mix.lock` | Locked dependency versions |
| `src/flagd-ui/Dockerfile` | Container build |

The flagd-ui service reads and writes `src/flagd/demo.flagd.json` (mounted as a volume). Changes to the JSON schema of that file affect flagd-ui behavior.

## OTel Instrumentation Patterns (Elixir / Phoenix)

### opentelemetry_exporter Library

The service uses the `opentelemetry_exporter` Elixir library for OTLP HTTP export. This is configured in `mix.exs` and `config/runtime.exs`:

```elixir
# mix.exs dependencies
{:opentelemetry_api, "~> 1.0"},
{:opentelemetry, "~> 1.0"},
{:opentelemetry_exporter, "~> 1.0"},
{:opentelemetry_phoenix, "~> 1.0"},
```

**Do not remove these dependencies.**

### OTLP HTTP Exporter Configuration

Configured in `config/runtime.exs` or via environment variables:

```
OTEL_EXPORTER_OTLP_ENDPOINT=http://otelcol:4318
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_SERVICE_NAME=flagd-ui
```

### Manual Spans (Elixir)

```elixir
require OpenTelemetry.Tracer, as: Tracer

Tracer.with_span "UpdateFlag" do
  Tracer.set_attributes([{"flag.name", flag_name}, {"flag.enabled", enabled}])
  # work here
end
```

### Phoenix LiveView Auto-Instrumentation

`opentelemetry_phoenix` auto-instruments Phoenix HTTP requests and LiveView lifecycle events. Do not remove its setup from the application supervisor or `Application.start/2`.

## flagd-ui Responsibilities

flagd-ui is the management UI for feature flags. It:
1. Reads `demo.flagd.json` to display current flag states.
2. Writes updates to `demo.flagd.json` when a user toggles a flag.
3. flagd (the daemon) watches the JSON file and hot-reloads it.

**Important**: Changes to how `demo.flagd.json` is read or written must not corrupt the file format — flagd will fail to parse an invalid JSON flag definition, breaking ALL feature flags across ALL services.

## Rules

1. **Preserve all OTel instrumentation.** Never remove `opentelemetry_exporter`, `opentelemetry_phoenix`, or manual span code.
2. **Never hide telemetry-impacting changes.** If your change affects what spans, metrics, or logs are emitted, state this explicitly in your output.
3. **Cite every changed file** in your output (absolute path).
4. **Run lint/build after changes:**
   - `mix compile` from `src/flagd-ui/`
   - `mix test` from `src/flagd-ui/` when tests exist
5. **Never corrupt `demo.flagd.json`** — validate JSON before writing. A corrupted flag file breaks telemetry across all services.
6. **Update `mix.lock`** by running `mix deps.get` after modifying `mix.exs`.

## Build and Test Commands

```bash
cd src/flagd-ui && mix compile
cd src/flagd-ui && mix test
cd src/flagd-ui && mix deps.get  # after mix.exs changes
```

## Common Pitfalls

- `demo.flagd.json` is shared between flagd-ui (writer) and flagd (reader) via a Docker volume mount — the path must match the mount configuration in docker-compose.
- An invalid `demo.flagd.json` (bad JSON, wrong schema) causes flagd to stop serving flags, breaking `emailMemoryLeak`, `adManualGc`, `recommendationCache`, and all other feature-flag-gated behaviors across the entire demo.
- Phoenix LiveView requires WebSocket support in the proxy — the Envoy config routes `/live` WebSocket connections to flagd-ui.
- `mix.lock` must be committed alongside `mix.exs` changes for reproducible builds.
- `OTEL_SERVICE_NAME` and `OTEL_EXPORTER_OTLP_ENDPOINT` come from docker-compose / K8s env — do not hardcode.

## Stop Behavior and Evidence Requirements

Do not claim task completion yourself.

When you stop, SubagentStop hooks will run deterministic gates automatically:
- `.sdd/evidence/changed-files.txt` is updated with all files you modified.
- `.sdd/evidence/review-router.latest.json` is written with the reviewer list for the orchestrator.

The root orchestrator will then dispatch reviewer agents based on what you changed.

### Before stopping, you must:
1. Cite every file you changed (with path from repo root).
2. State which OTel instrumentation was affected (if any).
3. Report whether build/lint/tests passed (with command used and result).
4. List any remaining work if you stopped early.

### Never:
- Claim "done" without running the relevant build command.
- Modify files outside your assigned service paths.
- Edit generated protobuf files (`.pb.go`, `demo_pb2.py`, `demo.ts`, etc.) by hand.
