# Checkout Flow - Overview

The checkout flow covers everything from adding an item to cart through placing an order and receiving a confirmation. It spans multiple services and includes both synchronous gRPC/HTTP calls and an asynchronous Kafka publish.

## Services involved

- **frontend** (Next.js) - cart page, checkout form, confirmation page
- **cart** (C# .NET, gRPC) - stores cart items in Valkey (Redis-compatible)
- **checkout** (Go gRPC) - orchestrates the full order placement
- **product-catalog** (Go gRPC) - resolves product prices per cart item
- **currency** (unknown) - converts prices to user currency
- **shipping** (Rust HTTP) - quotes shipping cost and creates tracking IDs
- **payment** (Node.js gRPC) - validates and charges credit card
- **email** (Ruby HTTP/Sinatra) - sends order confirmation email
- **kafka** - receives the order result for post-processing
- **accounting** (C# .NET) - Kafka consumer that processes completed orders

## User journey (summary)

1. User adds a product to cart from the product detail page.
2. User views cart at `/cart`; line items are shown with product details.
3. User fills the checkout form (address, email, credit card) and submits.
4. Frontend POSTs to `POST /api/checkout`.
5. Frontend gRPC-calls `CheckoutService.PlaceOrder`.
6. Checkout service orchestrates: fetches cart, resolves prices, quotes shipping, charges card, ships order, sends confirmation email, publishes to Kafka.
7. User is redirected to `/cart/checkout/{orderId}` showing order summary.

## Feature flags

| Flag | Effect |
|---|---|
| `cartFailure` | Routes `EmptyCart` to a bad store, causing it to fail |
| `paymentFailure` | Fails `PaymentService.Charge` at a configurable percentage (10% to 100%) |
| `paymentUnreachable` | Points checkout at `badAddress:50051` so payment is unreachable |
| `kafkaQueueProblems` | Sends N duplicate messages to Kafka after the real order, overloading the queue |
| `failedReadinessProbe` | Marks the cart service readiness probe as failed |
