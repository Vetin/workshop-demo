# frontend

## Identity

- **Language**: TypeScript
- **Framework**: Next.js 14 (Node.js SSR + React browser)
- **Port**: 8080 (`FRONTEND_PORT`)
- **Dockerfile**: `src/frontend/Dockerfile`
- **Main entry point**: `src/frontend/pages/index.tsx`

## Responsibility

The primary user-facing storefront. Renders product listings, cart, checkout flow, and recommendations. Makes gRPC calls to backend services server-side; sends OTLP traces directly from the browser client-side.

## Dependencies

All connections are direct (not through frontend-proxy):

| Dependency | Protocol | Purpose |
|---|---|---|
| ad | gRPC | `AdService.GetAds` — contextual ads |
| cart | gRPC | `CartService.{AddItem,GetCart,EmptyCart}` |
| checkout | gRPC | `CheckoutService.PlaceOrder` |
| currency | gRPC | `CurrencyService.{GetSupportedCurrencies,Convert}` |
| product-catalog | gRPC | `ProductCatalogService.{ListProducts,GetProduct}` |
| product-reviews | gRPC | `ProductReviewService.{GetProductReviews,GetAverageProductReviewScore,AskProductAIAssistant}` |
| recommendation | gRPC | `RecommendationService.ListRecommendations` |
| shipping | HTTP | Get shipping cost quote |
| image-provider | HTTP (proxied via frontend-proxy `/images/`) | Product images |
| flagd | gRPC (OpenFeature SDK) | Feature flags |

Environment variables: `FRONTEND_PORT`, `AD_ADDR`, `CART_ADDR`, `CHECKOUT_ADDR`, `CURRENCY_ADDR`, `PRODUCT_CATALOG_ADDR`, `PRODUCT_REVIEWS_ADDR`, `RECOMMENDATION_ADDR`, `SHIPPING_ADDR`, `FLAGD_HOST`, `FLAGD_PORT`.

## OTel Instrumentation

**Server-side (Node.js)**:
- `src/frontend/utils/telemetry/Instrumentation.js` — `@opentelemetry/sdk-node` with `getNodeAutoInstrumentations()`.
- OTLP gRPC exporters for traces and metrics.

**Browser-side**:
- `PUBLIC_OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://localhost:8080/otlp-http/v1/traces` routes browser spans through frontend-proxy to otel-collector.
- `WEB_OTEL_SERVICE_NAME=frontend-web` gives browser spans a distinct service name.

## gRPC Gateway Files

All gRPC client wrappers are in `src/frontend/gateways/rpc/`:
- `Ad.gateway.ts` — uses `AD_ADDR`
- `Cart.gateway.ts` — uses `CART_ADDR`
- `Checkout.gateway.ts` — uses `CHECKOUT_ADDR`
- `Currency.gateway.ts` — uses `CURRENCY_ADDR`
- `ProductCatalog.gateway.ts` — uses `PRODUCT_CATALOG_ADDR`
- `ProductReview.gateway.ts` — uses `PRODUCT_REVIEWS_ADDR`
- `Recommendations.gateway.ts` — uses `RECOMMENDATION_ADDR`

All use `@grpc/grpc-js` with `ChannelCredentials.createInsecure()`.

## Key Source Files

- `src/frontend/pages/` — Next.js page components and API routes
- `src/frontend/gateways/rpc/` — gRPC client wrappers
- `src/frontend/gateways/Api.gateway.ts` — HTTP API gateway for browser
- `src/frontend/utils/telemetry/Instrumentation.js` — server-side OTel setup
- `src/frontend/protos/demo.ts` — generated TypeScript stubs (from `pb/demo.proto`)
- `src/frontend/Dockerfile`

## Risky Notes

1. The TypeScript protobuf stubs in `src/frontend/protos/` are generated files. Changes to `pb/demo.proto` must trigger regeneration; there is no automated check in CI that verifies they are current.
2. Shipping is called via HTTP from `src/frontend/gateways/Api.gateway.ts` (not gRPC), even though `ShippingService` is in the proto.
3. The browser sends traces directly to `PUBLIC_OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`. If `ENVOY_PORT` changes, this URL must also change.
