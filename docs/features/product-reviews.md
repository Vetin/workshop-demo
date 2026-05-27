# Feature: Product Reviews

## Behavior

Each product detail page shows a review panel with: an AI assistant text input, an average star rating, a score distribution bar chart, and individual review cards. The AI assistant answers free-text questions about the product by calling an LLM that has access to the review data and product metadata.

## Services involved

| Service | Language | Role |
|---|---|---|
| frontend | TypeScript/Next.js | Renders `ProductReviews` component; fires review and AI-assistant API calls |
| product-reviews | Python | gRPC - fetches reviews from PostgreSQL; calls LLM for AI assistant |
| llm | mock or OpenAI-compatible | Generates natural-language answers |
| product-catalog | Go | gRPC - queried by product-reviews for product metadata (LLM tool call) |
| postgresql | - | Stores reviews in `reviews.productreviews` table |

## Key API calls

| Step | Call |
|---|---|
| Load reviews | `GET /api/product-reviews/{productId}` → gRPC `ProductReviewService.GetProductReviews` |
| Load average score | `GET /api/product-reviews-avg-score/{productId}` → gRPC `ProductReviewService.GetAverageProductReviewScore` |
| Ask AI | `POST /api/product-ask-ai-assistant/{productId}` → gRPC `ProductReviewService.AskProductAIAssistant` |

## Telemetry

- **Spans**: manual spans `get_product_reviews`, `get_average_product_review_score`, `get_ai_assistant_response` in product-reviews
- **Span attributes**: `app.product.id`, `app.product_reviews.count`, `app.product_reviews.average_score`, `app.product.question`
- **Error recording**: `span.record_exception(e)` and `span.set_status(ERROR)` on LLM rate limit errors
- **Metrics**: `app_product_review_counter` (labelled `product.id`); `app_ai_assistant_counter` (labelled `product.id`)

## Feature flags

| Flag | Effect |
|---|---|
| `llmRateLimitError` | With 50% probability, routes the AI request to `astronomy-llm-rate-limit` model, which returns a 429 error. Error is recorded on the span. |
| `llmInaccurateResponse` | For product ID `L9ECAV7KIM`, injects a prompt asking the LLM to produce an inaccurate answer. |

## Source paths

- `src/frontend/pages/product/[productId]/index.tsx`
- `src/frontend/providers/ProductReview.provider.tsx`
- `src/frontend/providers/ProductAIAssistant.provider.tsx`
- `src/frontend/pages/api/product-reviews/[productId]/index.ts`
- `src/frontend/pages/api/product-reviews-avg-score/[productId]/index.ts`
- `src/frontend/pages/api/product-ask-ai-assistant/[productId]/index.ts`
- `src/frontend/gateways/rpc/ProductReview.gateway.ts`
- `src/product-reviews/product_reviews_server.py`
- `src/product-reviews/database.py`
- `src/product-reviews/metrics.py`
