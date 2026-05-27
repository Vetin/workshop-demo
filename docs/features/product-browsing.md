# Feature: Product Browsing

## Behavior

Users can browse all products on the home page (`/`) and view details on `/product/{productId}`. Prices are displayed in the user's selected currency. Each product detail page also shows ads, recommendations, and product reviews.

## Services involved

| Service | Role |
|---|---|
| frontend | Renders pages; calls downstream services via `/api/*` BFF routes |
| product-catalog | gRPC - serves product list and individual products from PostgreSQL (`catalog.products`) |
| currency | gRPC - converts USD prices to the selected currency |
| ad | gRPC - returns contextual ads based on product categories |
| recommendation | gRPC - returns "You May Also Like" product IDs |

## Key API calls

| Step | Call |
|---|---|
| Home page load | `GET /api/products?currencyCode=` → gRPC `ProductCatalogService.ListProducts` |
| Product detail load | `GET /api/products/{productId}?currencyCode=` → gRPC `ProductCatalogService.GetProduct` |
| Currency conversion | gRPC `CurrencyService.Convert` (one call per product, skipped for USD) |

## Telemetry

- **Spans**: auto-instrumented gRPC server spans on product-catalog; SQL spans via `otelsql`; `InstrumentationMiddleware` on every frontend API route
- **Span attributes**: `app.products.count`, `app.product.id`, `app.product.name`, `app.products_search.count`
- **Metrics**: `app.frontend.requests` counter (frontend); DB connection pool stats (product-catalog)
- **Logs**: `"Product Found"` with `app.product.id` and `app.product.name` (product-catalog, otelslog)

## Feature flags

| Flag | Effect |
|---|---|
| `productCatalogFailure` | Returns an internal error for product ID `OLJCESPC7Z` when enabled |
| `imageSlowLoad` | Delays frontend image loading (`5sec` or `10sec`) |

## Source paths

- `src/frontend/pages/index.tsx`
- `src/frontend/pages/product/[productId]/index.tsx`
- `src/frontend/pages/api/products/index.ts`
- `src/frontend/pages/api/products/[productId]/index.ts`
- `src/frontend/services/ProductCatalog.service.ts`
- `src/product-catalog/main.go`
