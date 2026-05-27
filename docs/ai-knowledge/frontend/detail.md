# Frontend Architecture Detail

**Last updated:** 2026-05-27
**Source path:** `src/frontend/`

---

## Route / Page Structure

| URL Pattern | File | Key behaviour |
|---|---|---|
| `/` | `pages/index.tsx` | Fetches product list via `useQuery(['products', currency])`. Renders `Banner` + `ProductList`. |
| `/product/[productId]` | `pages/product/[productId]/index.tsx` | Fetches single product. Wraps page in `AdProvider` (keyed on product categories). Mounts `ProductAIAssistantProvider` and `ProductReviewProvider` as nested context. |
| `/cart` | `pages/cart/index.tsx` | Reads cart from `CartProvider` context. Shows `CartDetail` (items + checkout form) or `EmptyCart`. |
| `/cart/checkout/[orderId]` | `pages/cart/checkout/[orderId]/index.tsx` | Order confirmation page. Order data arrives as a JSON-serialised query param (`?order=...`). Computes totals client-side. |

---

## API Routes (BFF Layer)

All handlers call `InstrumentationMiddleware(handler)` before export. All gRPC addresses come from server-side `process.env.*_ADDR`.

| Route | Method(s) | Downstream | Notes |
|---|---|---|---|
| `GET/POST/DELETE /api/cart` | GET, POST, DELETE | `CartServiceClient` (gRPC, `CART_ADDR`) | GET enriches items with product details + currency conversion |
| `POST /api/checkout` | POST | `CheckoutServiceClient` (gRPC, `CHECKOUT_ADDR`) | Returns enriched order with product details per line item |
| `GET /api/currency` | GET | `CurrencyServiceClient` (gRPC, `CURRENCY_ADDR`) | Returns list of supported currency codes |
| `GET /api/shipping` | GET | `ShippingGateway` (HTTP POST to `SHIPPING_ADDR/get-quote`) + `CurrencyGateway` | Converts shipping cost to selected currency |
| `GET /api/data` | GET | `AdServiceClient` (gRPC, `AD_ADDR`) | Returns ads by context keys |
| `GET /api/recommendations` | GET | `RecommendationsServiceClient` (gRPC, `RECOMMENDATION_ADDR`) | Slices to 4 products, enriches with catalog + currency |
| `GET /api/products` | GET | `ProductCatalogService` | Lists all products with currency-converted prices |
| `GET /api/products/[productId]` | GET | `ProductCatalogService` | Single product with currency-converted price |
| `GET /api/product-reviews/[productId]` | GET | `ProductReviewServiceClient` (gRPC, `PRODUCT_REVIEWS_ADDR`) | Returns `ProductReview[]` |
| `GET /api/product-reviews-avg-score/[productId]` | GET | `ProductReviewServiceClient` (gRPC) | Returns average score string |
| `POST /api/product-ask-ai-assistant/[productId]` | POST | `ProductReviewServiceClient` (gRPC) `askProductAiAssistant` | AI Q&A; body: `{ question: string }` |

### Downstream Gateway Map

```
pages/api/* (BFF) ──┬── gateways/rpc/Cart.gateway.ts          → CART_ADDR (gRPC)
                    ├── gateways/rpc/Checkout.gateway.ts       → CHECKOUT_ADDR (gRPC)
                    ├── gateways/rpc/Currency.gateway.ts       → CURRENCY_ADDR (gRPC)
                    ├── gateways/rpc/Ad.gateway.ts             → AD_ADDR (gRPC)
                    ├── gateways/rpc/Recommendations.gateway.ts → RECOMMENDATION_ADDR (gRPC)
                    ├── gateways/rpc/ProductCatalog.gateway.ts → PRODUCT_CATALOG_ADDR (gRPC)
                    ├── gateways/rpc/ProductReview.gateway.ts  → PRODUCT_REVIEWS_ADDR (gRPC)
                    └── gateways/http/Shipping.gateway.ts      → SHIPPING_ADDR/get-quote (HTTP)
```

The `services/ProductCatalog.service.ts` and `services/ProductReview.service.ts` thin-orchestrate gateway calls (e.g. currency conversion after catalog fetch) and are called by API route handlers.

---

## Client-Side Data Layer

`gateways/Api.gateway.ts` is the only fetch client used by browser code. It:
- Calls `/api/*` (relative URLs — same origin, no CORS)
- Wraps every method in an OTel context that propagates W3C baggage with `app.session.id`
- Uses `utils/Request.ts` as the underlying fetch wrapper

Browser state is layered as React Query cache on top of these methods. Query keys always include `selectedCurrency` so stale data is re-fetched on currency switch.

---

## Component Inventory

### Layout

| Component | Path | Purpose |
|---|---|---|
| `Layout` | `components/Layout/` | Page shell — renders Header + main content + Footer |
| `Header` | `components/Header/` | App bar with logo, `CurrencySwitcher`, `CartIcon`, `PlatformFlag` |
| `Footer` | `components/Footer/` | Static footer |
| `Banner` | `components/Banner/` | Hero banner on home page |

### Commerce

| Component | Path | Purpose |
|---|---|---|
| `ProductList` | `components/ProductList/` | Grid of `ProductCard` items |
| `ProductCard` | `components/ProductCard/` | Single product tile with price, links to product detail |
| `ProductPrice` | `components/ProductPrice/` | Formats `Money` proto into currency string |
| `CartIcon` | `components/CartIcon/` | Cart icon with item count badge |
| `CartDropdown` | `components/CartDropdown/` | Dropdown preview of cart items |
| `CartItems` | `components/CartItems/` | Full cart item list used in cart page |
| `Cart/CartDetail` | `components/Cart/CartDetail.tsx` | Cart page main panel — combines `CartItems` + `CheckoutForm`; calls `placeOrder` on submit |
| `Cart/EmptyCart` | `components/Cart/EmptyCart.tsx` | Empty-state UI |
| `CheckoutItem` | `components/CheckoutItem/` | Line item row in the order confirmation page |
| `CheckoutForm` | `components/CheckoutForm/` | Full shipping + payment form (see Form Patterns below) |

### Discovery

| Component | Path | Purpose |
|---|---|---|
| `Recommendations` | `components/Recommendations/` | Horizontal list of recommended products; reads from `AdProvider` context |
| `Ad` | `components/Ad/` | Renders first ad from `AdProvider` context |
| `ProductReviews` | `components/ProductReviews/` | Review summary (average score, distribution bar chart, individual review cards) + AI assistant panel |

### Primitives / Shared

| Component | Path | Purpose |
|---|---|---|
| `Button` | `components/Button/` | Styled button (no variants prop — styling done via `$type` prop in some usages) |
| `Input` | `components/Input/` | Polymorphic input — renders `<input>` or `<select>` based on `type` prop |
| `Select` | `components/Select/` | Standalone styled `<select>` |
| `CurrencySwitcher` | `components/CurrencySwitcher/` | Calls `setSelectedCurrency` from `Currency.provider` |
| `PlatformFlag` | `components/PlatformFlag/` | Reads `NEXT_PUBLIC_PLATFORM` from `window.ENV` and displays it |

---

## Styling Conventions

- Every component folder contains a `ComponentName.styled.ts` file that exports named styled primitives (e.g. `S.Container`, `S.Title`).
- Page-level layout styles live in `styles/` (e.g. `styles/Cart.styled.ts`), imported as `* as S`.
- `styles/Theme.ts` defines a `DefaultTheme`-typed object with:
  - `colors`: 9 named values (`otelBlue`, `otelYellow`, `otelGray`, `backgroundGray`, etc.)
  - `breakpoints`: single `desktop` breakpoint at `768px`
  - `sizes`: 9 named sizes covering mobile/desktop scale
  - `fonts`: 4 weight tokens (`bold`, `regular`, `semiBold`, `light`)
- `styles/style.d.ts` augments the `DefaultTheme` type so TypeScript enforces theme shape.
- `globals.css` only handles body/html reset, font-family (`Open Sans`), and flex column for the root `#__next` container.
- No utility classes, no Tailwind.

---

## Form Patterns

There is one form in the application: `CheckoutForm`.

- **Uncontrolled-style controlled state:** a single `useState<IFormData>` holds all fields. `handleChange` is a single handler keyed on `e.target.name`.
- **No form library** (no React Hook Form, no Formik).
- **Validation:** HTML5 `required` and `pattern` attributes on `<input>` elements. No custom error display.
- **Pre-filled defaults** are hardcoded in the initial state (demo data only — not production values).
- Form delegates submission to the parent via an `onSubmit(formData: IFormData)` prop.
- `CheckoutForm` uses the shared `Input` component which unifies `<input>` and `<select>` rendering behind one component boundary.
- Cypress `data-cy` attributes (`CypressFields.CheckoutPlaceOrder`) are added on the submit button and key interactive elements throughout the app.

---

## Error and Loading States

| Context | Handling |
|---|---|
| TanStack Query (general) | No global error boundary found; individual components default to empty arrays/objects (`data ?? []`). |
| `ProductReviewProvider` | Exposes `loading`, `error` fields. `productReviews` is `null` while loading, `[]` when loaded but empty. |
| `ProductReviews` component | Renders `<p>Loading product reviews…</p>` and `<p>Could not load product reviews.</p>` inline. |
| `ProductAIAssistantProvider` | Exposes `aiLoading`, `aiError` via mutation state. `ProductReviews` renders an error paragraph and disables the Ask button during load. |
| API routes | Errors inside handlers are caught by `InstrumentationMiddleware` which records OTel exceptions, sets span status ERROR, and re-throws. The browser sees a 500 response. |
| `Cart/EmptyCart` | Shown when cart `items.length === 0`. |

There is no React Error Boundary component in the codebase.

---

## OpenTelemetry Browser Instrumentation Details

### FrontendTracer (`utils/telemetry/FrontendTracer.ts`)

- `WebTracerProvider` with two span processors:
  1. `SessionIdProcessor` — stamps `app.session.id` on every span start
  2. `BatchSpanProcessor` over `OTLPTraceExporter` (HTTP) — flushes every 500 ms
- `ZoneContextManager` (async context via zone.js)
- Propagators: `W3CBaggagePropagator` + `W3CTraceContextPropagator`
- Auto-instrumented via `getWebAutoInstrumentations`, specifically `@opentelemetry/instrumentation-fetch` with:
  - `propagateTraceHeaderCorsUrls: /.*/` (all URLs)
  - `applyCustomAttributesOnSpan` sets `app.synthetic_request` from `window.ENV.IS_SYNTHETIC_REQUEST`

### SessionIdProcessor (`utils/telemetry/SessionIdProcessor.ts`)

Implements `SpanProcessor`. On `onStart`, sets `app.session.id` attribute using the userId read from `localStorage` at module init time.

### Server-side Node SDK (`utils/telemetry/Instrumentation.js`)

Loaded via `NODE_OPTIONS='--require ./utils/telemetry/Instrumentation.js'` in `dev` script. Uses OTLP gRPC exporters with all cloud resource detectors. Instrumentation is the full `getNodeAutoInstrumentations` set minus `fs`.

### Api.gateway.ts OTel baggage propagation

Every API method is wrapped in a Proxy that injects the session ID into W3C Baggage before each call. This connects browser fetch spans to downstream service spans via trace context.

---

## Feature Flag Consumption

`_app.tsx` initialises `OpenFeature` with:
- Context: `{ targetingKey: userId, userId }` — set before provider init
- Provider: `FlagdWebProvider` connecting to `window.location.hostname` + current port + path prefix `/flagservice`
- TLS and port are derived from `window.location.protocol` and `window.location.port`

Components use `@openfeature/react-sdk` hooks. The `flagd-web-provider` connects over WebSocket; `maxRetries: 3`, `maxDelay: 10000ms`.

---

## Test and Story Availability

- **Cypress e2e** (3 suites):
  - `cypress/e2e/Home.cy.ts` — home page smoke tests
  - `cypress/e2e/ProductDetail.cy.ts` — product detail page
  - `cypress/e2e/Checkout.cy.ts` — full add-to-cart → place-order flow
- **No unit tests** (no Jest, no Vitest config found)
- **No Storybook**
- Cypress `data-cy` attributes are defined in `utils/enums/CypressFields.ts` and applied consistently across components

---

## Areas Suitable for UI-Kit Extraction

The following components are presentational with no direct context or API coupling and could be extracted into a shared library:

| Component | Reason |
|---|---|
| `Button` | No business logic; takes children + HTML button props |
| `Input` | Polymorphic `<input>`/`<select>` with label; reusable form primitive |
| `Select` | Styled select wrapper |
| `ProductPrice` | Pure formatting component — takes a `Money` proto and returns a formatted string |
| `Theme` + styled-components setup | Color/size/font tokens are already isolated in `styles/Theme.ts` |
| `StarRating` (inside `ProductReviews`) | Pure display component, not exported but extraction is trivial |

`Header`, `Footer`, `Layout`, and `Banner` have some coupling to routing and context but could be extracted with prop-injection of the cart count and currency switcher.
