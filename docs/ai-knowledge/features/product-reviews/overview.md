# Product Reviews - Overview

The product reviews feature lets users view community reviews and an average score for any product. It also exposes an AI assistant that answers natural-language questions about the product using an LLM backed by review data.

## Services involved

- **frontend** (Next.js) - renders the `ProductReviews` component on the product detail page
- **product-reviews** (Python gRPC) - serves reviews from PostgreSQL and proxies LLM requests
- **llm** (mock or OpenAI-compatible) - generates AI-assistant answers
- **product-catalog** (Go gRPC) - queried by product-reviews to fetch product metadata for LLM context
- **postgresql** - stores review rows in the `reviews.productreviews` table

## User journey (summary)

1. User opens any product detail page.
2. Frontend fires two parallel requests: `GET /api/product-reviews/{productId}` and `GET /api/product-reviews-avg-score/{productId}`.
3. Reviews and average score are displayed in the `ProductReviews` component.
4. User types a question and clicks "Ask"; frontend POSTs to `POST /api/product-ask-ai-assistant/{productId}`.
5. The AI assistant response is shown below the input.

## Feature flags

| Flag | Effect |
|---|---|
| `llmRateLimitError` | With 50% probability, routes the LLM call to `astronomy-llm-rate-limit` model which returns a 429 error |
| `llmInaccurateResponse` | For product ID `L9ECAV7KIM`, instructs the LLM to return an inaccurate answer |
