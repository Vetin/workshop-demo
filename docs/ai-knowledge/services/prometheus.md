# prometheus

## Identity

- **Language**: N/A
- **Framework**: Prometheus v3.8.1
- **Port**: 9090 (`PROMETHEUS_PORT`)
- **Dockerfile**: None — uses upstream `${PROMETHEUS_IMAGE}`
- **Main entry point**: `src/prometheus/prometheus-config.yaml`

## Responsibility

Metrics storage backend. Receives metrics from otel-collector and provides data to Grafana. OTLP receiver is enabled, allowing metrics to be pushed directly in addition to scraping.

## Key Configuration

- `--web.enable-otlp-receiver` — accepts OTLP metrics push.
- `--enable-feature=exemplar-storage` — stores exemplars (links from metrics to traces).
- `--storage.tsdb.retention.time=7d` — 7-day metric retention.

## Key Source Files

- `src/prometheus/prometheus-config.yaml` — scrape configs and remote write settings

## Risky Notes

Exemplar storage requires Grafana to be configured with exemplar queries pointing to Jaeger. If Jaeger's trace URL template changes, exemplar links in Grafana dashboards will break.
