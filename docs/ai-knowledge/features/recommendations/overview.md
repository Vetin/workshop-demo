# Recommendations - Overview

The "You May Also Like" panel appears at the bottom of product detail pages, the cart page, and the order confirmation page. It shows up to 4 products that are not currently in the user's context.

## Services involved

- **frontend** (Next.js) - `AdProvider` fires the recommendations request; `Recommendations` component renders results
- **recommendation** (Python gRPC) - selects product IDs to recommend, using the full catalog minus the given IDs
- **product-catalog** (Go gRPC) - resolves full product data for the recommended IDs
- **currency** (unknown) - converts prices when a non-USD currency is selected

## User journey (summary)

1. `AdProvider` mounts on any page that passes `productIds` and `contextKeys` as props.
2. `AdProvider` calls `ApiGateway.listRecommendations(productIds, selectedCurrency)` → `GET /api/recommendations?productIds=&sessionId=&currencyCode=`.
3. The frontend API route calls `RecommendationService.ListRecommendations(sessionId, productIds)` → gRPC `RecommendationService.ListRecommendations`.
4. The recommendation service fetches the full catalog from product-catalog, removes the provided `productIds`, and returns a random sample of up to 5 IDs.
5. The frontend API route takes up to 4 of those IDs and resolves each to a full `Product` via `ProductCatalogService.getProduct`.
6. The `Recommendations` component renders the resulting product cards.

## Feature flags

| Flag | Effect |
|---|---|
| `recommendationCacheFailure` | Simulates a cache leak: the service retains the catalog in a growing global list (`cached_ids`) and doubles its tail on each cache miss. On cache hit the stale list is used. Causes unbounded memory growth. |
