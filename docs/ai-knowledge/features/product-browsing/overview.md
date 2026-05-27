# Product Browsing - Overview

Users browse a product catalog from the home page or navigate directly to a product detail page. Prices are shown in the user's selected currency. Each product page also surfaces ads, recommendations, and reviews.

## Services involved

- **frontend** (Next.js) - renders home page and product detail page
- **product-catalog** (Go gRPC) - lists and fetches product data from PostgreSQL
- **currency** (unknown language) - converts prices to the user's chosen currency
- **ad** (Java) - returns contextual ads on product pages
- **recommendation** (Python gRPC) - provides "You May Also Like" product IDs

## User journey (summary)

1. User opens the home page; frontend calls `GET /api/products` to load the product grid.
2. User clicks a product; frontend calls `GET /api/products/{productId}` to load detail.
3. Product detail page fires parallel requests for ads, recommendations, reviews, and average review score.
4. User selects a quantity and clicks "Add To Cart".

## Feature flags

| Flag | Effect |
|---|---|
| `productCatalogFailure` | Causes `GetProduct` to return an error for product ID `OLJCESPC7Z` |
| `imageSlowLoad` | Delays frontend image loading by 5 or 10 seconds |
