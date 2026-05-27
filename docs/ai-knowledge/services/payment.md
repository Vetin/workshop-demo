# payment

## Identity

- **Language**: JavaScript (Node.js)
- **Framework**: gRPC (`@grpc/grpc-js`)
- **Port**: 50051 (`PAYMENT_PORT`)
- **Dockerfile**: `src/payment/Dockerfile`
- **Main entry point**: `src/payment/index.js`

## Responsibility

Charges credit cards. Exposes `PaymentService.Charge` gRPC method. In the demo the charge is simulated (no real payment processor).

## Dependencies

| Dependency | Protocol | Purpose |
|---|---|---|
| flagd | gRPC (OpenFeature) | Feature flags (payment failures scenario) |
| otel-collector | OTLP gRPC | Telemetry export |

Environment variables: `PAYMENT_PORT`, `IPV6_ENABLED`, `FLAGD_HOST`, `FLAGD_PORT`.

## OTel Instrumentation

- **Approach**: `@opentelemetry/sdk-node` with `getNodeAutoInstrumentations()` in `src/payment/opentelemetry.js`.
- Registered as `--require ./opentelemetry.js` before `index.js` (see Dockerfile `ENTRYPOINT`).
- **Manual**: `opentelemetry.trace.getActiveSpan()` used in `index.js` to add `app.payment.amount` attribute.
- **Exporters**: `OTLPTraceExporter` (gRPC), `OTLPMetricExporter` (gRPC) with `PeriodicExportingMetricReader`.
- Resource detectors: container, env, host, OS, process, AWS, GCP, Alibaba.

## gRPC Interface

Proto definition at `pb/demo.proto`:
```
service PaymentService {
    rpc Charge(ChargeRequest) returns (ChargeResponse) {}
}
```
Callers: checkout (`src/checkout/main.go` line 147 `paymentSvcClient`).

## Key Source Files

- `src/payment/index.js` — gRPC server + handler
- `src/payment/charge.js` — charge logic
- `src/payment/opentelemetry.js` — OTel SDK setup
- `src/payment/logger.js` — structured logger
- `src/payment/Dockerfile`

## Risky Notes

The proto file is loaded at runtime from `demo.proto` in the working directory (index.js line 38: `protoLoader.loadSync('demo.proto')`). If the file is missing at container runtime, the service fails to start with a file-not-found error rather than a compile error.
