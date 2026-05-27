# Rust Language Knowledge

Services: `src/shipping/`

## Version and Toolchain

- Rust latest stable (pinned via `rust-toolchain.toml` if present, otherwise
  `stable` channel)
- Cargo for build and dependency management

## Commands

| Task | Command | Working Directory |
|---|---|---|
| Build (debug) | `cargo build` | `src/shipping/` |
| Build (release) | `cargo build --release` | `src/shipping/` |
| Test | `cargo test` | `src/shipping/` |
| Lint | `cargo clippy -- -D warnings` | `src/shipping/` |
| Format | `cargo fmt` | `src/shipping/` |
| Check only | `cargo check` | `src/shipping/` |

`-D warnings` in clippy promotes all warnings to errors — the CI gate uses
this; ensure it passes before merging.

## OpenTelemetry Instrumentation

Actix-web middleware handles HTTP-level tracing:

```rust
use opentelemetry_instrumentation_actix_web::{RequestTracing, RequestMetrics};

App::new()
    .wrap(RequestTracing::new())
    .wrap(RequestMetrics::default())
```

OTLP gRPC exporter configured at startup via env vars:
- `OTEL_EXPORTER_OTLP_ENDPOINT`
- `OTEL_SERVICE_NAME`

For manual spans within handlers:

```rust
use opentelemetry::trace::Tracer;
use opentelemetry::global;

let tracer = global::tracer("shipping");
let span = tracer.start("calculate_quote");
// ...
span.end();
```

The `tracing` crate is used for structured logging; log macros (`tracing::info!`,
`tracing::error!`) are preferred over `println!`.

## Key Rust Idioms

- Return `Result<T, E>` from all fallible functions — never use `panic!` or
  `.unwrap()` in production request handlers.
- Use `?` operator to propagate errors up the call stack.
- RAII for resource management — no manual `drop()` calls needed in normal
  flows; rely on `Drop` trait.
- Smart pointers: `Arc<T>` for shared ownership across threads, `Box<T>` for
  heap allocation with single ownership. Avoid raw pointers (`*const T`,
  `*mut T`) in application code.
- Prefer `&str` over `String` in function parameters where ownership is not
  needed.

## Common Failure Modes

| Symptom | Root Cause |
|---|---|
| `thread 'main' panicked at 'called unwrap() on None'` | `.unwrap()` on `Option`/`Result` from env var or external call |
| Spans not emitted | `OTEL_EXPORTER_OTLP_ENDPOINT` env var not set or OTLP collector not reachable |
| Clippy CI failure | New code introduces `clippy::unwrap_used` or other lints promoted to errors |
| Build failure | Cargo dependency version conflict — run `cargo update` and verify `Cargo.lock` |
| HTTP 500 with no span | Error path returned without `span.set_status(StatusCode::Error, ...)` |

## Implementer Rules

1. No `.unwrap()` or `.expect()` in handler code or functions called from
   handlers — return `Result` and propagate with `?`.
2. Always set span status on error paths:
   ```rust
   span.set_status(opentelemetry::trace::StatusCode::Error, err.to_string());
   span.end();
   ```
3. Do not introduce `unsafe` blocks without explicit justification in the spec.
4. Keep `Cargo.lock` committed — the Docker build depends on it for
   reproducibility.

## Reviewer Checks

- `.unwrap()` or `.expect()` in handler or business logic code.
- Missing `span.set_status` and `span.record_exception` on error paths.
- `span.end()` missing (silently drops the span).
- Raw pointers (`*const`, `*mut`) in non-FFI code.
- `println!` / `eprintln!` instead of `tracing::info!` / `tracing::error!`.
- Cargo dependency version pins removed or replaced with `*`.
- `unsafe` block added without comment explaining why it is sound.
