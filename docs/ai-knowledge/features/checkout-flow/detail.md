# Checkout Flow - Detail

## Add to Cart

File: `src/frontend/pages/product/[productId]/index.tsx`

The "Add To Cart" button calls `Cart.provider.addItem({ productId, quantity })`, which calls `ApiGateway.addCartItem(...)` → `POST /api/cart` with body `{ item: { productId, quantity }, userId }`.

The frontend API route `src/frontend/pages/api/cart.ts` calls `CartGateway.addItem(userId, item)` → gRPC `CartService.AddItem(AddItemRequest)` on `CART_ADDR`.

Cart service (`src/cart/src/services/CartService.cs`) stores the item in Valkey via `ICartStore.AddItemAsync`.

Telemetry in CartService.AddItem:
- Span attributes: `app.user.id`, `app.product.id`, `app.product.quantity`

## View Cart

`GET /api/cart?sessionId=&currencyCode=` calls `CartGateway.getCart(sessionId)` → gRPC `CartService.GetCart(GetCartRequest)`.

For each cart item, the frontend also calls `ProductCatalogService.getProduct(productId, currencyCode)` to resolve the product details and currency-converted price.

Telemetry in CartService.GetCart:
- Span attributes: `app.user.id`, `app.cart.items.count`
- Span event: `"Fetch cart"`

## Place Order

File: `src/frontend/components/Cart/CartDetail.tsx`

On form submit, calls `Cart.provider.placeOrder(...)` → `ApiGateway.placeOrder(...)` → `POST /api/checkout?currencyCode=`.

The frontend API route at `src/frontend/pages/api/checkout.ts`:
1. Calls `CheckoutGateway.placeOrder(orderData)` → gRPC `CheckoutService.PlaceOrder(PlaceOrderRequest)` on `CHECKOUT_ADDR`.
2. For each returned order item, calls `ProductCatalogService.getProduct(productId, currencyCode)` to hydrate product details.

### CheckoutService.PlaceOrder (src/checkout/main.go)

This is the core orchestration. Steps in order:

1. **Get cart**: gRPC `CartService.GetCart(GetCartRequest{UserId})` on `CART_ADDR`
2. **Resolve product prices**: gRPC `ProductCatalogService.GetProduct(GetProductRequest{Id})` on `PRODUCT_CATALOG_ADDR` per item
3. **Convert prices to user currency**: gRPC `CurrencyService.Convert(CurrencyConversionRequest)` on `CURRENCY_ADDR`
4. **Get shipping quote**: `POST {SHIPPING_ADDR}/get-quote` with JSON body `{address, items}` (HTTP, not gRPC)
5. **Convert shipping to user currency**: gRPC `CurrencyService.Convert`
6. **Charge credit card**: gRPC `PaymentService.Charge(ChargeRequest{amount, creditCard})` on `PAYMENT_ADDR`
   - If `paymentUnreachable` flag is on, uses `badAddress:50051` instead
7. **Ship order**: `POST {SHIPPING_ADDR}/ship-order` with JSON body `{address, items}` → returns `tracking_id`
8. **Empty cart**: gRPC `CartService.EmptyCart(EmptyCartRequest{UserId})`
9. **Send confirmation email**: `POST {EMAIL_ADDR}/send_order_confirmation` with JSON body `{email, order, gift_message}` (when `gift_wrap=true`; `gift_message` is a top-level field, omitted when `gift_wrap=false`)
10. **Publish to Kafka** (only if `KAFKA_ADDR` is set): publishes protobuf-serialized `OrderResult` to the Kafka topic

Span attributes set in PlaceOrder:
- `app.user.id`, `app.user.currency`
- `app.order.id` (UUID)
- `app.shipping.amount` (float64)
- `app.order.amount` (float64)
- `app.order.items.count` (int)
- `app.shipping.tracking.id`
- `app.order.gift_wrap` (bool, always set on every PlaceOrder call)
- `app.order.gift_wrap.amount` (float64, set only when `gift_wrap=true`; value is the $5 fee converted to user currency)
- Span events: `"prepared"`, `"charged"` (with `app.payment.transaction.id`), `"shipped"` (with `app.shipping.tracking.id`), `"gift_wrap_fee_applied"` (only when `gift_wrap=true`)

Span attributes set in `prepareOrderItemsAndShippingQuoteFromCart`:
- `app.shipping.amount`, `app.cart.items.count`, `app.order.items.count`

Log messages from PlaceOrder:
- `"[PlaceOrder]"` with `user_id`, `user_currency`
- `"payment went through"` with `transaction_id`
- `"order placed"` with `app.order.id`, `app.shipping.amount`, `app.order.amount`, `app.order.items.count`, `app.shipping.tracking.id`
- `"failed to send order confirmation"` (warn, non-fatal)
- `"order confirmation email sent"` (info)
- `"sending to postProcessor"` (info)

### Kafka producer span (src/checkout/main.go)

`createProducerSpan` creates a producer span with:
- `peer.service: kafka`
- `network.transport: tcp`
- `messaging.system: kafka`
- `messaging.destination.name: {topic}`
- `messaging.operation: publish`
- `messaging.kafka.destination.partition`

On success, adds: `messaging.kafka.producer.success: true`, `messaging.kafka.producer.duration_ms`.

### Payment service (src/payment/charge.js)

Checks `paymentFailure` feature flag (float, 0–1). If `Math.random() < flagValue`, throws with `app.loyalty.level=gold`.

Span attributes set:
- `app.payment.amount`
- `app.payment.card_type`, `app.payment.card_valid`
- `app.loyalty.level` (random from `platinum|gold|silver|bronze`, or `gold` on failure)
- `app.payment.charged` (false if baggage contains `synthetic_request=true`, otherwise true)

Metric: counter `app.payment.transactions` with label `app.payment.currency`.

### Shipping service (src/shipping/src/shipping_service.rs)

Two HTTP POST endpoints: `/get-quote` and `/ship-order`. No gRPC — checkout calls these via `otelhttp.Post` (Go's HTTP client wrapped with OTel tracing).

## Order confirmation page

File: `src/frontend/pages/cart/checkout/[orderId]/index.tsx`

Rendered on the client from query params (`?order=<JSON>`). Shows order ID, shipping address, item list, shipping cost, and total. No additional API calls.

When `giftWrap=true` on the `OrderResult`, a gift wrap fee row is rendered:
`<S.SummaryRow><span>Gift Wrap:</span><ProductPrice price={giftWrapCost} /></S.SummaryRow>`.
The `orderTotal` useMemo includes `giftWrapCost?.units` and `giftWrapCost?.nanos` so the
grand total reflects the gift wrap charge.

## EmptyCart and cartFailure flag

`CartService.EmptyCart` (`src/cart/src/services/CartService.cs`) checks the `cartFailure` feature flag. If enabled, it calls `_badCartStore.EmptyCartAsync`, which causes an RPC error. The activity records the exception and sets `ActivityStatusCode.Error`.
