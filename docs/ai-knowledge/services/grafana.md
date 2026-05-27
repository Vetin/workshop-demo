# grafana

## Identity

- **Language**: N/A
- **Framework**: Grafana 12.3.1
- **Port**: 3000 (`GRAFANA_PORT`)
- **Dockerfile**: None — uses upstream `${GRAFANA_IMAGE}`
- **Main entry point**: `src/grafana/grafana.ini`

## Responsibility

Metrics and logs visualization dashboard. Pre-provisioned with datasources and dashboards for the demo. Accessible through frontend-proxy at `/grafana/`.

## Provisioned Datasources

Located in `src/grafana/provisioning/datasources/`:
- Prometheus (metrics)
- Jaeger (traces)
- OpenSearch (logs, using `grafana-opensearch-datasource` plugin)

## Key Source Files

- `src/grafana/grafana.ini` — Grafana configuration
- `src/grafana/provisioning/` — auto-provisioned datasources and dashboards

## Risky Notes

The `GF_INSTALL_PLUGINS=grafana-opensearch-datasource` plugin is installed at container startup by downloading from the internet. In air-gapped environments, this will fail silently and OpenSearch log queries will not work.
