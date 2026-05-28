# checkout

## Identity

- **Language**: Go
- **Framework**: gRPC Go + Sarama (Kafka producer) + net/http
- **Port**: 5050 (`CHECKOUT_PORT`)
- **Dockerfile**: `src/checkout/Dockerfile`
- **Main entry point**: `src/checkout/main.go`

## Responsibility

Orchestrates the full purchase flow: validates cart, converts currency, charges payment, arranges shipping, sends confirmation email, and emits an `orders` Kafka event for downstream consumers (accounting, fraud-detection).

## Dependencies

| Dependency | Protocol | Purpose |
|---|---|---|
| cart | gRPC | Retrieve and empty user cart |
| currency | gRPC | Convert prices |
| email | HTTP (JSON) | Send order confirmation |
| payment | gRPC | Charge credit card |
| product-catalog | gRPC | Get product details |
| shipping | HTTP | Get shipping quote + ship order |
| kafka | Kafka producer | Publish `orders` topic |
| flagd | gRPC (FlagdProvider) | Feature flags |
| otel-collector | OTLP gRPC | Telemetry export |

Environment variables: `CHECKOUT_PORT`, `CART_ADDR`, `CURRENCY_ADDR`, `EMAIL_ADDR`, `PAYMENT_ADDR`, `PRODUCT_CATALOG_ADDR`, `SHIPPING_ADDR`, `KAFKA_ADDR`, `FLAGD_HOST`, `FLAGD_PORT`.

## OTel Instrumentation

- **Approach**: OpenTelemetry Go SDK configured manually in `src/checkout/main.go`.
- **Libraries**: `otelgrpc` for all gRPC client connections (line 33), `otelhttp` for HTTP calls (line 34), `otelslog` bridge for structured logging (line 32), `runtime` instrumentation (line 35).
- **Exporters**: OTLP gRPC for traces, metrics, and logs (lines 90–132 of main.go).
- **Propagation**: W3C TraceContext + Baggage (line 99).
- **OpenFeature**: `otelhooks.NewTracesHook()` added (line 195).

## Kafka Producer Details

- Producer implementation: `src/checkout/kafka/producer.go` using IBM/sarama library
- Topic: `orders`
- Message value: protobuf-encoded `OrderResult`
- Protocol version: Sarama `V3_0_0_0`
- Acks: `NoResponse` (fire-and-forget, noted as intentional in producer.go line 40)

## gRPC Interface

Proto definition at `pb/demo.proto`:
```
service CheckoutService {
    rpc PlaceOrder(PlaceOrderRequest) returns (PlaceOrderResponse) {}
}
```
Callers: frontend (`src/frontend/gateways/rpc/Checkout.gateway.ts`).

### PlaceOrderRequest fields

```
string user_id       = 1
string user_currency = 2
Address address      = 3
string email         = 5
CreditCardInfo credit_card = 6
bool   gift_wrap     = 7
string gift_message  = 8
```

### OrderResult fields

```
string order_id              = 1
string shipping_tracking_id  = 2
Money  shipping_cost         = 3
Address shipping_address     = 4
repeated OrderItem items     = 5
bool   gift_wrap             = 6
Money  gift_wrap_cost        = 7
```

## Gift Wrap Logic (src/checkout/main.go)

When `PlaceOrderRequest.GiftWrap` is true:
- A fixed $5 USD fee is converted to the user's currency via `CurrencyService.Convert`.
- `OrderResult.GiftWrap` is set to `true` and `OrderResult.GiftWrapCost` is populated.
- The `gift_wrap_fee_applied` span event is emitted on the `PlaceOrder` span.
- `app.order.gift_wrap.amount` (float64) span attribute is set to the converted fee value.

`app.order.gift_wrap` (bool) is set on every `PlaceOrder` span regardless of whether gift wrap is selected.

`sendOrderConfirmation` now accepts a `giftMessage string` parameter. The gift message is
passed to the email service only when `gift_wrap=true` and is never recorded in any span
attribute, span event, log body field, or metric label (PII constraint).

## Key Source Files

- `src/checkout/main.go` — entry point, all service client setup, OTel bootstrap
- `src/checkout/kafka/producer.go` — Kafka async producer
- `src/checkout/money/` — currency math utilities
- `src/checkout/genproto/` — generated protobuf stubs
- `src/checkout/Dockerfile`

## Risky Notes

1. Kafka producer uses `NoResponse` acks — failed message delivery is silently ignored (producer.go line 41 comment confirms this tradeoff).
2. Email is called via HTTP (`EMAIL_ADDR=http://email:6060`), not gRPC, even though `EmailService` is defined in the proto. Any TLS or schema change on the email side needs separate tracking.
3. Shipping is also HTTP (`SHIPPING_ADDR=http://shipping:50050`), not gRPC.
