# Product Reviews - Detail

## Frontend wiring

File: `src/frontend/pages/product/[productId]/index.tsx`

The product detail page wraps its review section in two nested providers:

```tsx
<ProductAIAssistantProvider productId={productId}>
  <ProductReviewProvider productId={productId}>
    <ProductReviews />
  </ProductReviewProvider>
</ProductAIAssistantProvider>
```

`ProductReviewProvider` (`src/frontend/providers/ProductReview.provider.tsx`) fires two `useQuery` calls on mount:
- `ApiGateway.getProductReviews(productId)` → `GET /api/product-reviews/{productId}`
- `ApiGateway.getAverageProductReviewScore(productId)` → `GET /api/product-reviews-avg-score/{productId}`

`ProductAIAssistantProvider` (`src/frontend/providers/ProductAIAssistant.provider.tsx`) exposes a `useMutation` that calls `ApiGateway.askProductAIAssistant(productId, question)` → `POST /api/product-ask-ai-assistant/{productId}`.

## Frontend API routes

- `src/frontend/pages/api/product-reviews/[productId]/index.ts` → `ProductReviewService.getProductReviews(productId)` → `ProductReviewGateway.getProductReviews(productId)` → gRPC `ProductReviewService.GetProductReviews(GetProductReviewsRequest)` on `PRODUCT_REVIEWS_ADDR`
- `src/frontend/pages/api/product-reviews-avg-score/[productId]/index.ts` → `ProductReviewService.getAverageProductReviewScore(productId)` → gRPC `ProductReviewService.GetAverageProductReviewScore(GetAverageProductReviewScoreRequest)`
- `src/frontend/pages/api/product-ask-ai-assistant/[productId]/index.ts` → `ProductReviewService.askProductAIAssistant(productId, question)` → gRPC `ProductReviewService.AskProductAIAssistant(AskProductAIAssistantRequest)`

All three routes are wrapped in `InstrumentationMiddleware` which records `app.frontend.requests` and sets `http.status_code`.

## product-reviews service

File: `src/product-reviews/product_reviews_server.py`

Language: Python. Starts on `PRODUCT_REVIEWS_PORT`. Connects to PostgreSQL via `DB_CONNECTION_STRING` and to `PRODUCT_CATALOG_ADDR` for LLM tool calls.

### GetProductReviews

Calls `fetch_product_reviews_from_db(product_id)`:

```sql
SELECT username, description, score FROM reviews.productreviews WHERE product_id = %s
```

Span: `get_product_reviews`
- `app.product.id`
- `app.product_reviews.count`

Metric: `app_product_review_counter` (unit: `reviews`) incremented by number of reviews returned, labelled with `product.id`.

### GetAverageProductReviewScore

Calls `fetch_avg_product_review_score_from_db(product_id)`:

```sql
SELECT AVG(score) FROM reviews.productreviews WHERE product_id = %s
```

Span: `get_average_product_review_score`
- `app.product.id`
- `app.product_reviews.average_score`

### AskProductAIAssistant

Span: `get_ai_assistant_response`
- `app.product.id`
- `app.product.question`

The LLM is called via the OpenAI Python SDK against `LLM_BASE_URL` with model `LLM_MODEL`.

The LLM is given two tools:
- `fetch_product_reviews(product_id)` - returns the raw rows from the reviews table as JSON
- `fetch_product_info(product_id)` - calls `product_catalog_stub.GetProduct(GetProductRequest{id})` gRPC and returns the result as JSON

Feature flag checks inside `get_ai_assistant_response`:

1. **`llmRateLimitError`**: if enabled, 50% of calls are routed to `astronomy-llm-rate-limit` model (the mock). The mock returns a 429. The exception is recorded via `span.record_exception(e)` and the span status is set to `ERROR`. The response string `"The system is unable to process your response. Please try again later."` is returned.

2. **`llmInaccurateResponse`**: if enabled and `product_id == "L9ECAV7KIM"`, the second LLM call is given a user message asking it to return an inaccurate answer. This simulates hallucination for observability demos.

Metric: `app_ai_assistant_counter` (unit: `summaries`) incremented by 1 per request, labelled with `product.id`.

## UI component

File: `src/frontend/components/ProductReviews/ProductReviews.tsx`

Displays:
- AI assistant section: free-text input, "Ask" button, three quick-prompt buttons ("Can you summarize the product reviews?", "What age(s) is this recommended for?", "Were there any negative reviews?")
- Average score badge and star rating (`StarRating` component)
- Score distribution bar chart (5 rows, one per star level, with percentage)
- Grid of individual review cards (username, star rating, review text)

The component uses the `CypressFields` enum for Cypress test selectors (`CypressFields.ProductReviews`, `"AskAISection"`, `"AskAIInput"`, `"AskAIButton"`, `"AIAnswer"`, `"AIError"`).
