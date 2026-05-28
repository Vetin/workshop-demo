# HTTP Communication Map

---

## HTTP Servers (inbound endpoints)

### shipping (Rust / actix-web)

Source: `src/shipping/src/shipping_service.rs`

| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| POST | `/get-quote` | `get_quote` | Returns shipping cost as `{ cost_usd: Money }` JSON |
| POST | `/ship-order` | `ship_order` | Returns `{ tracking_id: string }` JSON |

Port bound via `$SHIPPING_PORT` in `src/shipping/src/main.rs`.

### email (Ruby / Sinatra)

Source: `src/email/email_server.rb`

| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| POST | `/send_order_confirmation` | anonymous Sinatra block | Parses JSON body `{ email, order, gift_message }`, sends email via Pony. `gift_message` is a top-level field (not nested in `order`); omitted when `gift_wrap=false`. Never recorded in telemetry. |

Port bound via `$EMAIL_PORT`.

### quote (PHP / Slim)

Source: `src/quote/app/routes.php`

| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| POST | `/getquote` | `calculateQuote` | Accepts `{ numberOfItems }`, returns float as JSON |

Port bound via `$QUOTE_PORT`.

### llm (Python / Flask)

Source: `src/llm/app.py`

| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| POST | `/v1/chat/completions` | `chat_completions` | OpenAI-compatible chat completions endpoint (mock) |
| GET | `/v1/models` | `list_models` | Lists available models |

Port `8000` hardcoded in `src/llm/app.py:222`.

### frontend (Next.js API routes)

All routes in `src/frontend/pages/api/`.

| Method | Path | Source File | Downstream Call |
|--------|------|-------------|-----------------|
| GET | `/api/cart` | `pages/api/cart.ts` | gRPC CartService.GetCart, ProductCatalogService.GetProduct |
| POST | `/api/cart` | `pages/api/cart.ts` | gRPC CartService.AddItem, CartService.GetCart |
| DELETE | `/api/cart` | `pages/api/cart.ts` | gRPC CartService.EmptyCart |
| GET | `/api/currency` | `pages/api/currency.ts` | gRPC CurrencyService.GetSupportedCurrencies |
| GET | `/api/shipping` | `pages/api/shipping.ts` | HTTP POST shipping `/get-quote`, gRPC CurrencyService.Convert |
| POST | `/api/checkout` | `pages/api/checkout.ts` | gRPC CheckoutService.PlaceOrder, ProductCatalogService.GetProduct |
| GET | `/api/products` | `pages/api/products/index.ts` | gRPC ProductCatalogService.ListProducts |
| GET | `/api/products/[productId]` | `pages/api/products/[productId]/index.ts` | gRPC ProductCatalogService.GetProduct, CurrencyService.Convert |
| GET | `/api/recommendations` | `pages/api/recommendations.ts` | gRPC RecommendationService.ListRecommendations, ProductCatalogService.GetProduct |
| GET | `/api/data` | `pages/api/data.ts` | gRPC AdService.GetAds |
| GET | `/api/product-reviews/[productId]` | `pages/api/product-reviews/[productId]/index.ts` | gRPC ProductReviewService.GetProductReviews |
| GET | `/api/product-reviews-avg-score/[productId]` | `pages/api/product-reviews-avg-score/[productId]/index.ts` | gRPC ProductReviewService.GetAverageProductReviewScore |
| POST | `/api/product-ask-ai-assistant/[productId]` | `pages/api/product-ask-ai-assistant/[productId]/index.ts` | gRPC ProductReviewService.AskProductAiAssistant |

---

## HTTP Clients (outbound calls)

### checkout (Go)

Uses `otelhttp.Post()` from `go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp`.

| Target | Method | Path | Source Location | Request Body |
|--------|--------|------|-----------------|--------------|
| shipping | POST | `$SHIPPING_ADDR/get-quote` | `src/checkout/main.go:463` | `{ address, items }` JSON |
| shipping | POST | `$SHIPPING_ADDR/ship-order` | `src/checkout/main.go:583` | `{ address, items }` JSON |
| email | POST | `$EMAIL_ADDR/send_order_confirmation` | `src/checkout/main.go:604` | `{ email, order, gift_message }` JSON. `gift_message` omitted when `gift_wrap=false`. |

### shipping (Rust)

Uses `awc::Client` (actix-web client) instrumented with `ClientExt::trace_request()`.

| Target | Method | Path | Source Location | Request Body |
|--------|--------|------|-----------------|--------------|
| quote | POST | `$QUOTE_ADDR/getquote` | `src/shipping/src/shipping_service/quote.rs:48-63` | `{ numberOfItems: u32 }` JSON |

### frontend (TypeScript — browser-side API gateway)

Source: `src/frontend/gateways/Api.gateway.ts`

The browser calls Next.js BFF routes (same-origin `/api/*`). The `request()` utility in `src/frontend/utils/Request.ts` handles all outbound fetch calls.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/cart` | Fetch cart contents |
| POST | `/api/cart` | Add item to cart |
| DELETE | `/api/cart` | Empty cart |
| GET | `/api/currency` | List supported currencies |
| GET | `/api/shipping` | Get shipping cost |
| POST | `/api/checkout` | Place order |
| GET | `/api/products` | List all products |
| GET | `/api/products/{productId}` | Get single product |
| GET | `/api/recommendations` | List recommendations |
| GET | `/api/data` | Get ads |
| GET | `/api/product-reviews/{productId}` | Get product reviews |
| GET | `/api/product-reviews-avg-score/{productId}` | Get average review score |
| POST | `/api/product-ask-ai-assistant/{productId}` | Ask AI assistant |

### frontend HTTP gateway (shipping only)

Source: `src/frontend/gateways/http/Shipping.gateway.ts`

| Method | Path | Env Var | Description |
|--------|------|---------|-------------|
| POST | `$SHIPPING_ADDR/get-quote` | `SHIPPING_ADDR` | Fetch shipping quote (called server-side from `/api/shipping` handler) |

### product-reviews (Python / OpenAI client)

Source: `src/product-reviews/product_reviews_server.py:204,177`

Uses `openai.OpenAI` client which issues HTTP/HTTPS calls.

| Target | Method | Path | Env Var | Notes |
|--------|--------|------|---------|-------|
| llm (mock) | POST | `http://$LLM_HOST:$LLM_PORT/v1/chat/completions` | `LLM_HOST`, `LLM_PORT` | Used when `llmRateLimitError` flag enabled |
| LLM (real or mock) | POST | `$LLM_BASE_URL/chat/completions` | `LLM_BASE_URL` | Normal path for AI assistant requests |

### load-generator (Python / Locust)

Source: `src/load-generator/locustfile.py`

Issues HTTP calls to frontend-proxy (Envoy) at `$LOCUST_HOST`.

| Method | Path | Task |
|--------|------|------|
| GET | `/` | `index` |
| GET | `/api/products/{productId}` | `browse_product`, `add_to_cart` |
| GET | `/api/recommendations` | `get_recommendations` |
| GET | `/api/product-reviews/{productId}` | `get_product_reviews` |
| POST | `/api/product-ask-ai-assistant/{productId}` | `ask_product_ai_assistant` |
| GET | `/api/data/` | `get_ads` |
| GET | `/api/cart` | `view_cart` |
| POST | `/api/cart` | `add_to_cart` |
| POST | `/api/checkout` | `checkout` |

---

## Envoy (frontend-proxy) Routing

Source: `src/frontend-proxy/envoy.tmpl.yaml`

Envoy listens on `$ENVOY_PORT` and routes:

| Prefix/Path | Upstream Cluster | Notes |
|-------------|-----------------|-------|
| `/loadgen/` | `loadgen` (`$LOCUST_WEB_HOST:$LOCUST_WEB_PORT`) | Load generator UI |
| `/otlp-http/` | `opentelemetry_collector_http` | OTLP HTTP forwarding |
| `/jaeger/` | `jaeger` (`$JAEGER_HOST:$JAEGER_UI_PORT`) | Jaeger UI |
| `/grafana/` | `grafana` (`$GRAFANA_HOST:$GRAFANA_PORT`) | Grafana UI |
| `/images/` | `image-provider` | Rewritten to `/` |
| `/flagservice/` | `flagservice` (`$FLAGD_HOST:$FLAGD_PORT`) | Flag evaluation |
| `/feature` | `flagd-ui` | Feature flag management UI |
| `/` (catch-all) | `frontend` (`$FRONTEND_HOST:$FRONTEND_PORT`) | Main storefront |

---

## Data Transformations

### checkout → shipping (HTTP)

checkout serializes protobuf `Address` and `[]*CartItem` to a JSON object with snake_case keys:
`{ "address": {...}, "items": [...] }` at `src/checkout/main.go:455-462,576-580`.

The shipping service reads these fields directly from the JSON body via serde in Rust.

### frontend → shipping (HTTP)

`src/frontend/gateways/http/Shipping.gateway.ts` explicitly transforms camelCase proto fields to snake_case before calling shipping:
- `streetAddress` → `street_address`
- `zipCode` → `zip_code`
- `productId` → `product_id`

This transformation is at `src/frontend/gateways/http/Shipping.gateway.ts:9-14,18-22`.

### shipping → quote (HTTP)

Shipping sends `{ "numberOfItems": u32 }` and receives a bare float (e.g. `8.99`) as the response body. The float is parsed and converted to a `Quote { dollars, cents }` struct in `src/shipping/src/shipping_service/quote.rs:73-77`.

---

## Risky Patterns

1. **Double HTTP hop for shipping cost** — frontend calls `/api/shipping` (Next.js), which calls shipping `/get-quote`, which calls quote `/getquote`. A latency or failure anywhere in this chain is invisible to the caller without distributed tracing.

2. **checkout contacts email over plain HTTP POST** — `src/checkout/main.go:561`. Email failures are logged as warnings and do not fail the order, masking email delivery problems.

3. **camelCase/snake_case mismatch** — frontend explicitly transforms field names before calling shipping (`src/frontend/gateways/http/Shipping.gateway.ts:9-14`). checkout does the same transformation inline at `src/checkout/main.go:455-462`. If the shipping API schema ever changes, both callers need coordinated updates.

4. **product-reviews LLM URL selection** — `llmRateLimitError` feature flag changes which LLM URL is used (mock vs. real), with different base URLs (`LLM_HOST:LLM_PORT/v1` vs. `LLM_BASE_URL`). A misconfigured flag can silently redirect all LLM traffic to the mock.
