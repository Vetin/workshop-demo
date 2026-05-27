# Feature: Checkout Flow

## Behavior

Users add items to a cart backed by Valkey (Redis-compatible). From the cart page they submit a checkout form with shipping address, email, and credit card. The checkout service orchestrates the full order: price resolution, shipping quote, payment, cart clearing, confirmation email, and a Kafka publish. On success the user sees an order confirmation page.

## Services involved

| Service | Language | Role |
|---|---|---|
| frontend | TypeScript/Next.js | BFF routes, cart state, checkout form, confirmation page |
| cart | C# (.NET) | gRPC - stores/retrieves cart items in Valkey |
| checkout | Go | gRPC - orchestrates the entire PlaceOrder flow |
| product-catalog | Go | gRPC - resolves product prices per order item |
| currency | C++ | gRPC - converts prices and shipping cost to user currency |
| shipping | Rust | HTTP REST - quotes shipping cost and generates tracking IDs |
| payment | Node.js | gRPC - validates and charges the credit card |
| email | Ruby | HTTP/Sinatra - sends confirmation email |
| kafka | - | Message broker - receives serialized `OrderResult` |
| accounting | C# (.NET) | Kafka consumer - processes completed orders |

## Key API / gRPC calls in PlaceOrder

1. gRPC `CartService.GetCart`
2. gRPC `ProductCatalogService.GetProduct` (per item)
3. gRPC `CurrencyService.Convert` (per item price + shipping)
4. HTTP `POST {shipping}/get-quote`
5. gRPC `PaymentService.Charge`
6. HTTP `POST {shipping}/ship-order`
7. gRPC `CartService.EmptyCart`
8. HTTP `POST {email}/send_order_confirmation`
9. Kafka produce `orders` topic (protobuf `OrderResult`)

## Telemetry

- **Spans**: gRPC auto-instrumentation on all services; `otelhttp` on checkout's HTTP calls to shipping and email; manual `charge` span in payment; manual `send_email` span in email
- **Span attributes**: `app.user.id`, `app.user.currency`, `app.order.id`, `app.order.amount`, `app.order.items.count`, `app.shipping.amount`, `app.shipping.tracking.id`, `app.payment.transaction.id`, `app.payment.card_type`, `app.loyalty.level`, `app.cart.items.count`
- **Span events**: `"prepared"`, `"charged"`, `"shipped"` (checkout); `"Fetch cart"`, `"Empty cart"` (cart)
- **Kafka producer span**: `messaging.system=kafka`, `messaging.operation=publish`, `messaging.kafka.producer.success`, `messaging.kafka.producer.duration_ms`
- **Metrics**: `app.payment.transactions` counter (payment service, labelled by currency)
- **Logs**: structured logs at each checkout step with order/shipping/payment IDs

## Feature flags

| Flag | Effect |
|---|---|
| `cartFailure` | Routes `EmptyCart` to a bad store, causing RPC failure |
| `paymentFailure` | Fails `Charge` at 10%–100% probability |
| `paymentUnreachable` | Points checkout at `badAddress:50051` (connection failure) |
| `kafkaQueueProblems` | Sends N duplicate Kafka messages (N = flag integer value) |
| `failedReadinessProbe` | Marks cart service readiness probe as failed |

## Source paths

- `src/frontend/pages/api/cart.ts`
- `src/frontend/pages/api/checkout.ts`
- `src/frontend/components/Cart/CartDetail.tsx`
- `src/cart/src/services/CartService.cs`
- `src/checkout/main.go`
- `src/payment/charge.js`
- `src/shipping/src/shipping_service.rs`
- `src/email/email_server.rb`

---

> **Note**: This file was migrated from `docs/features/checkout-flow.md` (legacy flat file). The original flat file is kept as a redirect stub.
