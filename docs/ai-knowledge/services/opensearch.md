# opensearch

## Identity

- **Language**: N/A (Java/JVM under the hood)
- **Framework**: OpenSearch 3.4.0
- **Port**: 9200 (HTTP)
- **Dockerfile**: `src/opensearch/Dockerfile`
- **Main entry point**: N/A (standard OpenSearch node)

## Responsibility

Log storage backend. Receives structured logs from otel-collector and serves them to Grafana via the OpenSearch datasource plugin.

## Configuration

Single-node cluster:
- `discovery.type=single-node`
- `DISABLE_SECURITY_PLUGIN=true` — no auth required within the demo network
- `OPENSEARCH_JAVA_OPTS=-Xms400m -Xmx400m`

## Key Source Files

- `src/opensearch/Dockerfile` — extends upstream image (likely adds index templates)

## Risky Notes

1. Security plugin is disabled (`DISABLE_SECURITY_PLUGIN=true`). The OpenSearch HTTP port 9200 is accessible to any container in the `opentelemetry-demo` network without authentication.
2. No persistent volume is configured. All logs are lost on container restart.
3. The Grafana datasource config in `src/grafana/provisioning/datasources/opensearch.yaml` has a version comment that must be kept in sync with the `OPENSEARCH_IMAGE` version in `.env`.
