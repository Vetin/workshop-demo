# Feature Flags Reference

All flags are defined in `src/flagd/demo.flagd.json` and evaluated by flagd (OpenFeature provider). Services that consume them connect to flagd on `FLAGD_HOST:FLAGD_PORT` (default `flagd:8013`) using OpenFeature SDKs.

The flagd UI for toggling flags live is in `src/flagd-ui/`.

## Flags

| Flag name | Default | Variant type | Feature | Effect |
|---|---|---|---|---|
| `llmInaccurateResponse` | `off` (false) | bool | Product Reviews AI | For product ID `L9ECAV7KIM`, instructs the LLM to return an inaccurate answer |
| `llmRateLimitError` | `off` (false) | bool | Product Reviews AI | With 50% probability, routes the LLM call to `astronomy-llm-rate-limit` which returns a 429 error; exception is recorded on the span |
| `productCatalogFailure` | `off` (false) | bool | Product Browsing | Returns `codes.Internal` for product ID `OLJCESPC7Z` in `GetProduct`; sets span status to ERROR |
| `recommendationCacheFailure` | `off` (false) | bool | Recommendations | Activates simulated cache leak in recommendation service; each cache miss grows the global ID list |
| `adManualGc` | `off` (false) | bool | Ads | Triggers full manual garbage collections in the ad service (Java) |
| `adHighCpu` | `off` (false) | bool | Ads | Triggers high CPU load in the ad service (Java) |
| `adFailure` | `off` (false) | bool | Ads | Fails the ad service |
| `kafkaQueueProblems` | `off` (0) | int (100 when `on`) | Checkout | After publishing the real order, sends N duplicate Kafka messages; N = flag value |
| `cartFailure` | `off` (false) | bool | Checkout | Routes `CartService.EmptyCart` to a bad store, causing RPC failure |
| `paymentFailure` | `off` (0.0) | float | Checkout | Probability (0–1) of `PaymentService.Charge` throwing an error; variants: `10%`=0.1, `25%`=0.25, `50%`=0.5, `75%`=0.75, `90%`=0.95, `100%`=1 |
| `paymentUnreachable` | `off` (false) | bool | Checkout | Replaces the payment client address with `badAddress:50051`, causing a connection failure |
| `loadGeneratorFloodHomepage` | `off` (0) | int (100 when `on`) | Load Gen | Floods the frontend with a large number of requests |
| `imageSlowLoad` | `off` (0) | int (ms) | Product Browsing | Delays image loading in the frontend by 5000 or 10000 ms |
| `failedReadinessProbe` | `off` (false) | bool | Checkout | Causes the cart service readiness probe to fail |
| `emailMemoryLeak` | `off` (0) | int | Order Email | Multiplies email body size; accumulated deliveries are not cleared, causing memory growth |

## Which services consume each flag

| Flag | Consumer service | SDK |
|---|---|---|
| `llmInaccurateResponse` | product-reviews | Python openfeature + FlagdProvider |
| `llmRateLimitError` | product-reviews | Python openfeature + FlagdProvider |
| `productCatalogFailure` | product-catalog | Go openfeature + flagd provider |
| `recommendationCacheFailure` | recommendation | Python openfeature + FlagdProvider |
| `adManualGc` | ad | Java (unknown SDK) |
| `adHighCpu` | ad | Java (unknown SDK) |
| `adFailure` | ad | Java (unknown SDK) |
| `kafkaQueueProblems` | checkout | Go openfeature + flagd provider |
| `cartFailure` | cart | C# OpenFeature |
| `paymentFailure` | payment | Node.js `@openfeature/server-sdk` + FlagdProvider |
| `paymentUnreachable` | checkout | Go openfeature + flagd provider |
| `loadGeneratorFloodHomepage` | load-generator | Python (UNKNOWN - not verified) |
| `imageSlowLoad` | frontend | TypeScript (UNKNOWN - not verified in frontend code) |
| `failedReadinessProbe` | cart | C# OpenFeature (UNKNOWN - exact usage not verified) |
| `emailMemoryLeak` | email | Ruby `openfeature-flagd` gem |

Items marked UNKNOWN were not verified in source code during this documentation pass.
