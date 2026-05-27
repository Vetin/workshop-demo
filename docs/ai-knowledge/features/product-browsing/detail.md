# Product Browsing - Detail

## Home page

File: `src/frontend/pages/index.tsx`

On mount, the home page calls `ApiGateway.listProducts(selectedCurrency)`, which hits `GET /api/products`.

The Next.js API route at `src/frontend/pages/api/products/index.ts` calls `ProductCatalogService.listProducts(currencyCode)`.

`ProductCatalogService` (`src/frontend/services/ProductCatalog.service.ts`) calls two gRPC services:
- `ProductCatalogGateway.listProducts()` → gRPC `ProductCatalogService.ListProducts(Empty)` on `PRODUCT_CATALOG_ADDR`
- `CurrencyGateway.convert(price, currencyCode)` → gRPC `CurrencyService.Convert(CurrencyConversionRequest)` on `CURRENCY_ADDR` (once per product, skipped when currency is USD)

The product-catalog service (`src/product-catalog/main.go`) queries PostgreSQL:

```sql
SELECT p.id, p.name, p.description, p.picture,
       p.price_currency_code, p.price_units, p.price_nanos, p.categories
FROM catalog.products p ORDER BY p.id
```

## Product detail page

File: `src/frontend/pages/product/[productId]/index.tsx`

Calls `ApiGateway.getProduct(productId, selectedCurrency)` → `GET /api/products/{productId}` → `ProductCatalogService.getProduct(id, currencyCode)` → `ProductCatalogGateway.getProduct(id)` → gRPC `GetProduct(GetProductRequest{id})`.

The product-catalog service queries:

```sql
SELECT p.id, p.name, p.description, p.picture,
       p.price_currency_code, p.price_units, p.price_nanos, p.categories
FROM catalog.products p WHERE p.id = $1
```

The page wraps itself in `AdProvider` (which also fetches recommendations) and mounts `ProductReviews` and `Recommendations` components.

## Feature flag: productCatalogFailure

Checked in `src/product-catalog/main.go` `checkProductFailure()`. If the flag is `on` and `req.Id == "OLJCESPC7Z"`, the service returns `codes.Internal` with the message "Error: Product Catalog Fail Feature Flag Enabled". A span event and error status are set before returning.

## Telemetry emitted

### product-catalog (Go)

Spans:
- Auto-instrumented gRPC server span for each `ListProducts`, `GetProduct`, `SearchProducts` call (via `otelgrpc.NewServerHandler()`)
- SQL spans from `otelsql` for each database query

Span attributes set manually:
- `app.products.count` (int) on `ListProducts`
- `app.product.id` (string), `app.product.name` (string) on `GetProduct`
- `app.products_search.count` (int) on `SearchProducts`
- span event `"Product Found"` on successful `GetProduct`

Logs:
- `"Product Found"` with `app.product.name` and `app.product.id` via `otelslog`
- `"Found N products from database"` with `products` count

Metrics:
- DB connection pool stats registered via `otelsql.RegisterDBStatsMetrics`

### frontend (Next.js)

Every API route handler is wrapped with `InstrumentationMiddleware` (`src/frontend/utils/telemetry/InstrumentationMiddleware.ts`), which:
- Records a counter `app.frontend.requests` with labels `{ method, target, status }`
- Sets `http.status_code` on the active span

OTel baggage propagation: `ApiGateway` injects a `session.id` baggage entry on every outbound request (`src/frontend/gateways/Api.gateway.ts`).
