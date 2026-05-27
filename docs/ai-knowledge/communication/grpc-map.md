# gRPC Communication Map

Source of truth: `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/pb/demo.proto`

All services share a single proto package `oteldemo` defined in `pb/demo.proto`.

---

## gRPC Servers

| Service | Language | Proto Service | Listening on | Source |
|---------|----------|---------------|-------------|--------|
| ad | Java | AdService | `$AD_PORT` | `src/ad/src/main/java/oteldemo/AdService.java` |
| cart | C# (.NET) | CartService | `$CART_PORT` | `src/cart/src/services/CartService.cs` |
| checkout | Go | CheckoutService | `$CHECKOUT_PORT` | `src/checkout/main.go` |
| currency | C++ | CurrencyService | `$CURRENCY_PORT` | `src/currency/src/server.cpp` |
| email | Ruby (Sinatra HTTP) | EmailService via HTTP | `$EMAIL_PORT` | `src/email/email_server.rb` (see note) |
| payment | Node.js | PaymentService | `$PAYMENT_PORT` | `src/payment/index.js` |
| product-catalog | Go | ProductCatalogService | `$PRODUCT_CATALOG_PORT` | `src/product-catalog/main.go` |
| product-reviews | Python | ProductReviewService | `$PRODUCT_REVIEWS_PORT` | `src/product-reviews/product_reviews_server.py` |
| recommendation | Python | RecommendationService | `$RECOMMENDATION_PORT` | `src/recommendation/recommendation_server.py` |
| shipping | Rust (actix-web HTTP) | ShippingService via HTTP | `$SHIPPING_PORT` | `src/shipping/src/main.rs` (see note) |

Note: email and shipping expose HTTP endpoints, not gRPC. Checkout calls them over HTTP despite their proto definitions. See http-map.md.

---

## gRPC Clients

### frontend (TypeScript / Next.js)

All clients are in `src/frontend/gateways/rpc/`.

| Client File | Proto Service | Methods Called | Env Var |
|-------------|---------------|----------------|---------|
| `Ad.gateway.ts` | AdService | `GetAds` | `AD_ADDR` |
| `Cart.gateway.ts` | CartService | `GetCart`, `AddItem`, `EmptyCart` | `CART_ADDR` |
| `Checkout.gateway.ts` | CheckoutService | `PlaceOrder` | `CHECKOUT_ADDR` |
| `Currency.gateway.ts` | CurrencyService | `Convert`, `GetSupportedCurrencies` | `CURRENCY_ADDR` |
| `ProductCatalog.gateway.ts` | ProductCatalogService | `ListProducts`, `GetProduct` | `PRODUCT_CATALOG_ADDR` |
| `ProductReview.gateway.ts` | ProductReviewService | `GetProductReviews`, `GetAverageProductReviewScore`, `AskProductAiAssistant` | `PRODUCT_REVIEWS_ADDR` |
| `Recommendations.gateway.ts` | RecommendationService | `ListRecommendations` | `RECOMMENDATION_ADDR` |

### checkout (Go)

Client setup in `src/checkout/main.go` via `mustCreateClient()` / `grpc.NewClient()`.

| Target Service | Proto Service Client | Methods Called | Source Location |
|---------------|---------------------|----------------|-----------------|
| cart | CartServiceClient | `GetCart`, `EmptyCart` | `src/checkout/main.go:492-503` |
| product-catalog | ProductCatalogServiceClient | `GetProduct` | `src/checkout/main.go:510-512` |
| currency | CurrencyServiceClient | `Convert` | `src/checkout/main.go:525-533` |
| payment | PaymentServiceClient | `Charge` | `src/checkout/main.go:543-548` |

### recommendation (Python)

Client setup in `src/recommendation/recommendation_server.py`.

| Target Service | Stub Class | Methods Called | Source Location |
|---------------|-----------|----------------|-----------------|
| product-catalog | `ProductCatalogServiceStub` | `ListProducts`, `GetProduct` (via `GetProduct` in cache-miss branch) | `src/recommendation/recommendation_server.py:95-96,84` |

### product-reviews (Python)

Client setup in `src/product-reviews/product_reviews_server.py`.

| Target Service | Stub Class | Methods Called | Source Location |
|---------------|-----------|----------------|-----------------|
| product-catalog | `ProductCatalogServiceStub` | `GetProduct` (for `fetch_product_info` tool) | `src/product-reviews/product_reviews_server.py:314` |

---

## Full Caller → Callee gRPC Table

| Caller | Callee | Proto Service | RPC Method | Source Evidence |
|--------|--------|---------------|------------|-----------------|
| frontend | ad | AdService | `GetAds` | `src/frontend/gateways/rpc/Ad.gateway.ts:14` |
| frontend | cart | CartService | `GetCart`, `AddItem`, `EmptyCart` | `src/frontend/gateways/rpc/Cart.gateway.ts:13-26` |
| frontend | checkout | CheckoutService | `PlaceOrder` | `src/frontend/gateways/rpc/Checkout.gateway.ts:13` |
| frontend | currency | CurrencyService | `Convert`, `GetSupportedCurrencies` | `src/frontend/gateways/rpc/Currency.gateway.ts:12-18` |
| frontend | product-catalog | ProductCatalogService | `ListProducts`, `GetProduct` | `src/frontend/gateways/rpc/ProductCatalog.gateway.ts:12-20` |
| frontend | product-reviews | ProductReviewService | `GetProductReviews`, `GetAverageProductReviewScore`, `AskProductAiAssistant` | `src/frontend/gateways/rpc/ProductReview.gateway.ts:13-27` |
| frontend | recommendation | RecommendationService | `ListRecommendations` | `src/frontend/gateways/rpc/Recommendations.gateway.ts:12-16` |
| checkout | cart | CartService | `GetCart`, `EmptyCart` | `src/checkout/main.go:492,499` |
| checkout | product-catalog | ProductCatalogService | `GetProduct` | `src/checkout/main.go:510` |
| checkout | currency | CurrencyService | `Convert` | `src/checkout/main.go:526` |
| checkout | payment | PaymentService | `Charge` | `src/checkout/main.go:543` |
| recommendation | product-catalog | ProductCatalogService | `ListProducts`, `GetProduct` | `src/recommendation/recommendation_server.py:95,84` |
| product-reviews | product-catalog | ProductCatalogService | `GetProduct` | `src/product-reviews/product_reviews_server.py:314` |

---

## Generated Proto Code Locations

| Language | Location | Generator Command |
|----------|----------|-------------------|
| Go (checkout) | `src/checkout/genproto/oteldemo/` | `protoc --go_out=./ --go-grpc_out=./` (see `src/checkout/main.go:63`) |
| Go (product-catalog) | `src/product-catalog/genproto/oteldemo/` | `protoc --go_out=./ --go-grpc_out=./` (see `src/product-catalog/main.go:7`) |
| C++ (currency) | `src/currency/build/generated/proto/` | CMake build via `src/currency/genproto/CMakeLists.txt` |
| Python (recommendation) | `src/recommendation/demo_pb2.py`, `demo_pb2_grpc.py` | protoc with grpc_tools |
| Python (product-reviews) | `src/product-reviews/demo_pb2.py`, `demo_pb2_grpc.py` | protoc with grpc_tools |
| TypeScript (frontend) | `src/frontend/protos/demo.ts` | ts-proto / protoc-gen-ts |
| TypeScript (react-native-app) | `src/react-native-app/protos/demo.ts` | ts-proto / protoc-gen-ts |
| Node.js (payment) | runtime load via `grpc.loadPackageDefinition(protoLoader.loadSync('demo.proto'))` | `src/payment/index.js:38` |

---

## Risky Patterns

1. **Proto file is the single source of truth** — `pb/demo.proto` is manually copied or symlinked into each service. Any change to message fields risks breaking multiple generated files across 7+ languages simultaneously. There is no automated regeneration pipeline surfaced at the repo root.

2. **checkout calls email and shipping over HTTP, not gRPC** — despite EmailService and ShippingService having proto definitions, checkout uses `otelhttp.Post()` directly. The proto definitions for these two are unused by checkout. See `src/checkout/main.go:463,561,583`.

3. **payment loads proto at runtime** — `src/payment/index.js` uses `protoLoader.loadSync('demo.proto')` at startup, meaning a missing or mislocated proto file causes a runtime failure with no compile-time guard.

4. **recommendation has a cache-leak feature flag** — when `recommendationCacheFailure` is enabled, the `cached_ids` list grows unboundedly, changing which gRPC methods are called on product-catalog. See `src/recommendation/recommendation_server.py:79-87`.
