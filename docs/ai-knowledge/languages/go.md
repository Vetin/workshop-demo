# Go Language Knowledge

Services: `src/checkout/` (checkout), `src/product-catalog/` (product-catalog)

## Version and Toolchain

- Go 1.24+
- Modules managed via `go.mod` / `go.sum` in each service directory

## Commands

| Task | Command | Working Directory |
|---|---|---|
| Build | `go build ./...` | service directory |
| Test | `go test ./...` | service directory |
| Lint | `go vet ./...` | service directory |
| Format | `gofmt -w .` | service directory |

## OpenTelemetry Instrumentation Pattern

Both services use the manual OTel SDK. Key packages:

| Package | Usage |
|---|---|
| `go.opentelemetry.io/otel` | Core API (tracer, propagators) |
| `go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc` | gRPC interceptors |
| `go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp` | HTTP client/server wrapping |
| `go.opentelemetry.io/contrib/bridges/otelslog` | Structured log bridge (`otelslog`) |
| `github.com/XSAM/otelsql` | SQL instrumentation (product-catalog only) (third-party package, not the official OTel contrib path) |

OTLP exporter is configured via standard env vars (`OTEL_EXPORTER_OTLP_ENDPOINT`, etc.).

### gRPC server setup (both services)

Interceptors must be attached on both server and client:

```go
grpc.NewServer(
    grpc.StatsHandler(otelgrpc.NewServerHandler()),
)
grpc.Dial(addr,
    grpc.WithStatsHandler(otelgrpc.NewClientHandler()),
)
```

Never remove these interceptors — doing so silently drops all distributed
trace propagation for that service.

### Span lifecycle

```go
ctx, span := tracer.Start(ctx, "operationName")
defer span.End()
// ... work ...
if err != nil {
    span.RecordError(err)
    span.SetStatus(codes.Error, err.Error())
    return err
}
```

## Generated Proto Stubs

- checkout: `src/checkout/genproto/oteldemo/`
- product-catalog: `src/product-catalog/genproto/oteldemo/`

**Do not hand-edit these files.** Regenerate with:

```
make docker-generate-protobuf
```

After `pb/demo.proto` changes, regenerate and commit the generated files
together with the proto change.

## Key Go Idioms

- `context.Context` is always the first parameter of any function doing I/O or
  tracing — never drop context when calling into a traced subsystem.
- Error wrapping: `fmt.Errorf("describe what failed: %w", err)` — use `%w`
  so callers can use `errors.Is` / `errors.As`.
- No `panic` outside `main()` or package `init()` — return errors to callers.
- Prefer named return values only for documentation, not as a control flow
  shortcut.

## Common Failure Modes

| Symptom | Root Cause |
|---|---|
| Build fails with `go: inconsistent vendoring` | Stale `go.sum` — run `go mod tidy` |
| Traces missing for a downstream call | `context.Context` not threaded through; span not started before call |
| Span end never recorded | `defer span.End()` missing; span leaks into garbage collector |
| Metrics not exported | `OTEL_EXPORTER_OTLP_ENDPOINT` env var not set or OTLP listener not reachable |
| gRPC calls not linked across services | `otelgrpc` interceptor removed from server or client setup |

## Implementer Rules

1. Preserve `otelgrpc` interceptors on every gRPC server and client — removing
   them breaks distributed tracing across the whole demo.
2. Never remove `otelslog` bridge — it links log records to the active trace.
3. Always pass `context.Context` as first argument through the call chain.
4. Keep generated proto stubs in `genproto/` — do not inline generated types.

## Reviewer Checks

- Wrong or generic span names (e.g., `"handler"`) — names should be descriptive
  operation names matching the function or operation being performed (e.g.,
  `"prepareOrderItemsAndShippingQuoteFromCart"`). There is no mandatory
  `service.OperationName` prefix format; use the actual operation name.
- Missing `defer span.End()` after `tracer.Start`.
- `context.TODO()` left in committed code — should be `context.Background()` at
  app entry points or a propagated ctx elsewhere.
- `errors.New` used where `fmt.Errorf("...: %w", err)` is needed for error
  chain preservation.
- `otelgrpc` interceptors removed without replacement.
