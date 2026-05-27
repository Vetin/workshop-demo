# Recommendations - Detail

## Frontend wiring

File: `src/frontend/providers/Ad.provider.tsx`

`AdProvider` is used on three pages:
- `src/frontend/pages/product/[productId]/index.tsx` — passes current product ID plus IDs of items currently in cart; `contextKeys` is the product's categories
- `src/frontend/pages/cart/index.tsx` — passes all cart item product IDs; `contextKeys` from all cart item categories
- `src/frontend/pages/cart/checkout/[orderId]/index.tsx` — passes order item product IDs; `contextKeys` from item categories

The `AdProvider` fires a `useQuery` for recommendations:

```ts
queryKey: ['recommendations', productIds, 'selectedCurrency', selectedCurrency]
queryFn: () => ApiGateway.listRecommendations(productIds, selectedCurrency)
```

This calls `GET /api/recommendations?productIds=...&sessionId=...&currencyCode=...`.

## Frontend API route

File: `src/frontend/pages/api/recommendations.ts`

1. Calls `RecommendationsGateway.listRecommendations(sessionId, productIds)` → gRPC `RecommendationService.ListRecommendations(ListRecommendationsRequest{userId: sessionId, product_ids: productIds})` on `RECOMMENDATION_ADDR` (resolved via `src/frontend/gateways/rpc/Recommendations.gateway.ts`).
2. Takes `productList.slice(0, 4)` from the response.
3. Calls `ProductCatalogService.getProduct(id, currencyCode)` for each, which in turn calls `ProductCatalogGateway.getProduct` and `CurrencyGateway.convert` as needed.
4. Returns the array of hydrated `Product` objects.

## Recommendation service

File: `src/recommendation/recommendation_server.py`

Language: Python. Starts on `RECOMMENDATION_PORT`. Connects to `PRODUCT_CATALOG_ADDR` at startup.

### ListRecommendations

Calls `get_product_list(request.product_ids)`:

**Normal path (flag off)**:
```python
cat_response = product_catalog_stub.ListProducts(demo_pb2.Empty())
product_ids = [x.id for x in cat_response.products]
```
Removes the requested `product_ids` from the full list, then `random.sample` up to 5 IDs.

**recommendationCacheFailure path (flag on)**:
- 50% chance (or first run): cache miss. Calls `ListProducts`, appends results to the global `cached_ids`, then appends `cached_ids[:len(cached_ids) // 4]` again (grows the list each time). Sets `app.cache_hit=False`.
- Otherwise: cache hit, uses the already-growing `cached_ids`. Sets `app.cache_hit=True`.

Note: the `check_feature_flag` function hardcodes `"recommendationCacheFailure"` regardless of the `flag_name` argument passed in (apparent bug in `src/recommendation/recommendation_server.py` line 126).

### Span attributes

Set on the `get_product_list` span:
- `app.recommendation.cache_enabled` (bool)
- `app.cache_hit` (bool, only when cache enabled)
- `app.products.count` (int) - total IDs in pool
- `app.filtered_products.count` (int) - IDs after removing input products
- `app.filtered_products.list` (list of strings)

Set on the gRPC server span:
- `app.products_recommended.count` (int)

### Metrics

`app_recommendations_counter` (unit: `recommendations`) - incremented by the count of returned product IDs, labelled `recommendation.type: catalog`.

## Rendering

File: `src/frontend/components/Recommendations/Recommendations.tsx`

The component reads `recommendedProductList` from `AdProvider` context. Renders a "You May Also Like" heading and a grid of `ProductCard` components. Returns `null` if the list is empty.
