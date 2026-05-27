# Frontend Architecture Overview

**Last updated:** 2026-05-27
**Source path:** `src/frontend/`

## Framework and Runtime

- **Next.js** 16.1.1 (Pages Router — no App Router)
- **React** 19.2.3
- **TypeScript** 5.9.3
- Bundler: Turbopack (default in Next.js 16), Webpack available via `--webpack` flag
- Output mode: `standalone` (suitable for containerized deployment)

## Directory Layout

```
src/frontend/
  pages/           # Next.js Pages Router — routes and API handlers
    _app.tsx       # Root app wrapper (providers, OTel init, feature flags)
    _document.tsx  # Custom HTML document
    index.tsx      # Home / product listing
    cart/
      index.tsx
      checkout/[orderId]/index.tsx
    product/[productId]/index.tsx
    api/           # Server-side API routes (BFF layer)
  components/      # UI components, one folder per component
  providers/       # React context providers (Cart, Currency, Ad, Reviews, AI)
  gateways/        # Data-access layer
    Api.gateway.ts      # Client-side fetch wrapper (browser → /api/*)
    Session.gateway.ts  # localStorage session management
    rpc/           # Server-side gRPC stubs (used by API routes only)
    http/          # Server-side HTTP clients (Shipping)
  services/        # Server-side orchestration (currency conversion, etc.)
  utils/
    telemetry/     # OTel setup — FrontendTracer, Instrumentation.js, middleware
    enums/         # CypressFields, AttributeNames
  styles/          # Global CSS + per-page styled-components files + Theme
  types/           # TypeScript interfaces (Cart, etc.)
  protos/          # Generated gRPC types from demo.proto
  genproto/        # Protobuf generated sources
  cypress/         # E2E tests
```

## State Management

No Redux or Zustand. State is managed via two mechanisms:

1. **React Context providers** — Cart, Currency, Ad/Recommendations, ProductReview, ProductAIAssistant. Each exposes a typed context and a `use*` hook.
2. **TanStack React Query 5** — all remote data fetching and mutations go through `useQuery` / `useMutation`. `QueryClientProvider` is mounted in `_app.tsx`.

Session identity (UUID) is persisted in `localStorage` via `Session.gateway.ts`.

## Styling

- **styled-components** 6 (compiler plugin enabled in `next.config.js`)
- Each component has a co-located `*.styled.ts` file exporting styled primitives
- A single typed `Theme` object (`styles/Theme.ts`) provides colors, breakpoints, font weights, and size tokens
- One global CSS file (`styles/globals.css`) sets base resets only (font-family, box-sizing, flex column layout on `#__next`)
- No Tailwind, no CSS modules

## OpenTelemetry Instrumentation

Two separate OTel setups run side by side:

| Layer | File | What it does |
|---|---|---|
| Browser | `utils/telemetry/FrontendTracer.ts` | `WebTracerProvider` + OTLP HTTP exporter, auto-instrumentation of `fetch`, W3C propagators, `SessionIdProcessor` stamps session ID on every span |
| Node (SSR / API routes) | `utils/telemetry/Instrumentation.js` | `NodeSDK` with OTLP gRPC exporter, all node auto-instrumentations, cloud resource detectors |
| API route middleware | `utils/telemetry/InstrumentationMiddleware.ts` | Wraps every `/api/*` handler; records exceptions, sets `HTTP_STATUS_CODE`, increments `app.frontend.requests` counter |

Browser env vars are injected into `window.ENV` at runtime; the `FrontendTracer` reads from there.

## Feature Flags (OpenFeature / flagd)

- SDK: `@openfeature/react-sdk` + `@openfeature/flagd-web-provider`
- Provider is initialized in `_app.tsx`, connecting to flagd through the Envoy proxy (`/flagservice` path prefix) using the browser's current host and port
- Session context (`targetingKey: userId`) is set before provider init to avoid a second evaluation round-trip
- Components consume flags via `@openfeature/react-sdk` hooks

## API Layer (BFF Pattern)

All API routes sit under `pages/api/` and act as a Backend-for-Frontend (BFF). They translate REST calls from the browser into gRPC (or HTTP) calls to downstream services. Every handler is wrapped with `InstrumentationMiddleware`.

## Test Coverage

- **Cypress** e2e tests at `cypress/e2e/` (3 suites: Home, ProductDetail, Checkout)
- No Storybook, no unit tests (Jest / Vitest) found

## Local Commands

From `src/frontend/`:

| Command | Purpose |
|---|---|
| `npm run dev` | Development server with Node OTel instrumentation pre-loaded |
| `npm run build` | Production build |
| `npm run start` | Production server |
| `npm run lint` | ESLint |
| `npm run cy:open` | Opens Cypress interactive test runner |
| `npm run grpc:generate` | Regenerates protobuf TypeScript types from `demo.proto` |

## Environment Variables

Variables flow from the root `.env` file through `next.config.js`:

**Server-side only (passed to gRPC gateways):**
- `CART_ADDR`, `CHECKOUT_ADDR`, `CURRENCY_ADDR`, `PRODUCT_CATALOG_ADDR`, `PRODUCT_REVIEWS_ADDR`, `RECOMMENDATION_ADDR`, `AD_ADDR`, `SHIPPING_ADDR`
- `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`, `OTEL_SERVICE_NAME`

**Public (exposed to browser via `window.ENV`):**
- `NEXT_PUBLIC_PLATFORM` (from `ENV_PLATFORM`) — displayed by `PlatformFlag` component
- `NEXT_PUBLIC_OTEL_SERVICE_NAME`
- `NEXT_PUBLIC_OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` (from `PUBLIC_OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`)
- `IS_SYNTHETIC_REQUEST` — set on fetch spans as `app.synthetic_request`
