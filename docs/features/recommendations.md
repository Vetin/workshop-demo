# Feature: Recommendations

## Behavior

A "You May Also Like" panel appears at the bottom of the product detail page, cart page, and order confirmation page. It shows up to 4 products that are not already in the current context. The recommendation service excludes the provided product IDs, samples the remainder randomly, and returns up to 5 IDs; the frontend resolves up to 4 of those to full product objects.

## Services involved

| Service | Language | Role |
|---|---|---|
| frontend | TypeScript/Next.js | `AdProvider` fires the request; `Recommendations` component renders the product cards |
| recommendation | Python | gRPC - selects product IDs from the full catalog minus input IDs |
| product-catalog | Go | gRPC - resolves full product data for the recommended IDs |
| currency | unknown | gRPC - converts prices when non-USD currency is selected |

## Key API calls

| Step | Call |
|---|---|
| Fetch recommendations | `GET /api/recommendations?productIds=&sessionId=&currencyCode=` → gRPC `RecommendationService.ListRecommendations` |
| Resolve product details | gRPC `ProductCatalogService.GetProduct` (up to 4 calls) |
| Currency conversion | gRPC `CurrencyService.Convert` (when non-USD) |

## Telemetry

- **Spans**: auto-instrumented gRPC server span on recommendation service; manual `get_product_list` span inside `ListRecommendations`
- **Span attributes on `get_product_list`**: `app.recommendation.cache_enabled`, `app.cache_hit` (when cache mode active), `app.products.count`, `app.filtered_products.count`, `app.filtered_products.list`
- **Span attributes on server span**: `app.products_recommended.count`
- **Metrics**: `app_recommendations_counter` (unit: `recommendations`, labelled `recommendation.type: catalog`)

## Feature flags

| Flag | Effect |
|---|---|
| `recommendationCacheFailure` | Activates a simulated cache leak. On cache miss, appends the full catalog to a global list and then appends 25% of the list again, growing unboundedly. The span records `app.cache_hit` accordingly. |

## Source paths

- `src/frontend/providers/Ad.provider.tsx`
- `src/frontend/components/Recommendations/Recommendations.tsx`
- `src/frontend/pages/api/recommendations.ts`
- `src/frontend/gateways/rpc/Recommendations.gateway.ts`
- `src/recommendation/recommendation_server.py`
- `src/recommendation/metrics.py`
