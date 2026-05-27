# postgresql

## Identity

- **Language**: N/A
- **Framework**: PostgreSQL 17.6
- **Port**: 5432 (`POSTGRES_PORT`)
- **Dockerfile**: None — uses upstream `postgres:17.6` image
- **Main entry point**: `src/postgresql/init.sql` (initialization script mounted at container start)

## Responsibility

Relational database shared by accounting (order persistence) and product-catalog (product data) and product-reviews (review data).

## Dependencies

None.

Environment variables: `POSTGRES_USER=root`, `POSTGRES_PASSWORD`, `POSTGRES_DB`.

## Connection Strings

| Service | Connection string |
|---|---|
| accounting | `Host=${POSTGRES_HOST};Username=otelu;Password=otelp;Database=${POSTGRES_DB}` |
| product-catalog | `postgres://otelu:otelp@${POSTGRES_HOST}/${POSTGRES_DB}?sslmode=disable` |
| product-reviews | `host=${POSTGRES_HOST} user=otelu password=otelp dbname=${POSTGRES_DB}` |

## OTel Instrumentation

- No agent on the PostgreSQL container itself.
- Metrics scraped by the otel-collector `postgresql` receiver configured in `src/otel-collector/otelcol-config.yml` (lines 25–47).
- Collected metrics: `blks_hit`, `blks_read`, `tup_fetched`, `tup_returned`, `tup_inserted`, `tup_updated`, `tup_deleted`, `deadlocks`.
- product-catalog uses `otelsql` to trace individual SQL queries.

## Key Source Files

- `src/postgresql/init.sql` — schema initialization

## Risky Notes

The same database instance is shared by three services (accounting, product-catalog, product-reviews). Schema changes in `init.sql` affect all three. There is no migration framework — the init script only runs on a fresh volume.
