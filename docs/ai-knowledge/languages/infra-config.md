# Infrastructure / Config Language Knowledge

This file covers all configuration-only services in the OpenTelemetry Demo.
None of these services have application code — they are pure config files
interpreted by third-party daemons.

## flagd — Feature Flag Config

- Config file: `src/flagd/demo.flagd.json`
- Format: JSON, hot-reloaded by the flagd daemon (no restart needed)
- Schema pattern:

```json
{
  "flags": {
    "flagName": {
      "state": "ENABLED",
      "variants": {
        "on": true,
        "off": false
      },
      "defaultVariant": "off"
    }
  }
}
```

Rules:
- The file must be valid JSON at all times — an invalid JSON file breaks ALL
  feature flags for the entire demo, affecting every service that reads flags.
- Validate with `python3 -m json.tool src/flagd/demo.flagd.json` or any JSON
  linter before committing.
- Flag keys referenced in frontend code (`useFlag('key', default)`) must exactly
  match keys in this file. A mismatch silently returns the default value.
- `state` must be `"ENABLED"` or `"DISABLED"` — disabled flags always return
  `defaultVariant` without evaluating rules.

## frontend-proxy — Envoy

- Config template: `src/frontend-proxy/envoy.tmpl.yaml`
- Runtime processing: environment variable substitution (`${VAR}` syntax) at
  container startup using `envsubst`.
- Routes: HTTP, gRPC (HTTP/2), WebSocket — all handled by the single Envoy config.

Rules:
- Never commit the rendered config (the `envsubst` output) — only the template.
- `traceparent` header must be forwarded to downstream services; verify
  `x-b3-*` / `traceparent` headers are in the `request_headers_to_add` or
  forwarded via `headers_to_copy` in each route cluster.
- Changes to routing (path prefixes, cluster names) must be verified end-to-end
  — Envoy returns 404 silently if a route matcher is wrong.

## image-provider — nginx

- Config template: `src/image-provider/nginx.conf.template`
- Runtime processing: `envsubst` at container start.
- OTel: `ngx_otel_module` loaded for trace context injection into static responses.

Rules:
- Keep `ngx_otel_module` directive — removing it drops tracing for image serving.
- Do not add server-side logic (Lua, etc.) without explicit spec approval.

## otel-collector — OpenTelemetry Collector

- Main config: `src/otel-collector/otelcol-config.yml`
- Test config: `test/tracetesting/otelcol-config-tracetest.yml`
- Uses OpenTelemetry Collector Contrib image.

Config structure:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
      http:
processors:
  batch:
  memory_limiter:
exporters:
  otlp/jaeger:
  prometheusremotewrite:
  opensearch:
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/jaeger, opensearch]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheusremotewrite]
```

Rules:
- Never remove an existing pipeline entry without verifying there are no
  downstream consumers (dashboards, alerts, Tracetest tests) that depend on it.
- The Tracetest collector config is separate — do not merge them.
- `memory_limiter` processor must remain in pipelines — it prevents OOM crashes
  under load.
- Adding a new exporter requires adding it to at least one `service.pipelines`
  entry, or it is silently unused.

## Prometheus

- Config: `src/prometheus/prometheus-config.yaml`
- Scrape configs define which services are scraped for metrics.

Rules:
- Do not change scrape intervals without understanding the cardinality impact.
- New services exposing Prometheus metrics must be added as a scrape target.
- Recording rules and alerting rules should be in separate files loaded via
  `rule_files:`.

## Grafana

- Main config: `src/grafana/grafana.ini`
- Datasources: provisioned via `src/grafana/provisioning/datasources/`
- Dashboards: provisioned via `src/grafana/provisioning/dashboards/`

Rules:
- Dashboard JSON files are auto-provisioned — do not modify the provisioning
  directory structure.
- Do not store credentials in `grafana.ini` — use env vars (`GF_*`).

## Tracetest (Test Infrastructure)

- Tests: `test/tracetesting/`
- Each service has a YAML test spec referencing span names and attributes.
- Collector config: `test/tracetesting/otelcol-config-tracetest.yml`

Rules:
- If you rename a span or change a span attribute name in any service, update
  the corresponding Tracetest test spec in `test/tracetesting/`.
- Run `make run-tracetesting` to verify tests pass after span changes.

## Kubernetes Manifests

- Generated via Helm: `make generate-kubernetes-manifests`
- Output: `kubernetes/opentelemetry-demo.yaml` (generated — do not hand-edit)

Rules:
- After changing `docker-compose.yml` (service env vars, ports, volumes),
  run `make generate-kubernetes-manifests` to keep the Helm chart in sync.
- Never hand-edit `kubernetes/opentelemetry-demo.yaml` — it will be overwritten
  on the next `make generate-kubernetes-manifests` run.

## Kafka Config (`src/kafka/`)

- KRaft mode (no ZooKeeper)
- JMX scraper for metrics export to Prometheus
- Java agent for OTel: `KAFKA_OPTS=-javaagent:/usr/share/java/opentelemetry-javaagent.jar`

Rules:
- Do not change `KAFKA_CLUSTER_ID` after initial deployment — it is baked into
  the KRaft metadata.
- Topic creation is handled by `kafka-topics.sh` init scripts — do not create
  topics manually in the config.

## PostgreSQL (`src/postgresql/`)

- Initialization scripts in `src/postgresql/` (SQL files run at container start).
- Used exclusively by product-catalog service.

Rules:
- Schema migrations must be backward-compatible — the product-catalog service
  may roll before the DB migration runs.
- Never store sensitive data beyond what the demo requires.

## OpenSearch (`src/opensearch/`)

- Config files for index templates and lifecycle policies.
- Receives trace data from the OTel Collector `opensearch` exporter.

Rules:
- Index template changes must be compatible with existing collector exporter
  mapping — field type conflicts cause ingestion failures.
