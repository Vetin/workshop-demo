# flagd-ui

## Identity

- **Language**: Elixir
- **Framework**: Phoenix LiveView
- **Port**: 4000 (`FLAGD_UI_PORT`)
- **Dockerfile**: `src/flagd-ui/Dockerfile`
- **Main entry point**: `src/flagd-ui/lib/flagd_ui_web/router.ex`

## Responsibility

Web UI for managing feature flags in the demo. Allows toggling flags defined in `src/flagd/demo.flagd.json` without restarting services. Accessible through frontend-proxy at `/feature`.

## Dependencies

| Dependency | Protocol | Purpose |
|---|---|---|
| flagd | File (shared volume) | Reads/writes `demo.flagd.json` |
| otel-collector | OTLP HTTP | Telemetry export |

Environment variables: `FLAGD_UI_PORT`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `SECRET_KEY_BASE`, `PHX_HOST`.

## OTel Instrumentation

- **Approach**: `opentelemetry_exporter` Elixir library configured in `src/flagd-ui/mix.exs` (lines 16-22 as a release application).
- **Exporter**: OTLP HTTP (`http://${OTEL_COLLECTOR_HOST}:${OTEL_COLLECTOR_PORT_HTTP}`).

## Routes (from `src/flagd-ui/lib/flagd_ui_web/router.ex`)

- `GET /` — LiveView Dashboard (flag list with toggle controls)
- `GET /advanced` — Advanced Editor (raw JSON editor for flag file)
- `GET /api/...` — JSON API for flag operations

## Build

Elixir/Phoenix release built with `mix release`. Docker base image `hexpm/elixir:1.19.3-erlang-28.0.2-debian-bullseye`.

## Key Source Files

- `src/flagd-ui/lib/flagd_ui_web/router.ex` — HTTP routing
- `src/flagd-ui/lib/flagd_ui_web/live/` — LiveView modules
- `src/flagd-ui/mix.exs` — project configuration and OTel release config
- `src/flagd-ui/Dockerfile`

## Risky Notes

flagd-ui and flagd share `./src/flagd` as a volume mount. flagd-ui writes directly to the JSON file — there is no API between them. This is the only service pair that communicates via a shared filesystem rather than a network protocol.
