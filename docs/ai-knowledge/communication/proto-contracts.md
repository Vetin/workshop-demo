# Proto Contracts

This document maps every protobuf definition in the repo to the services that implement or consume it.

---

## Source files

| File | Role |
|------|------|
| `pb/demo.proto` | Single source of truth for all application-level service contracts (package `oteldemo`) |
| `src/currency/proto/grpc/health/v1/health.proto` | gRPC standard health-check protocol (package `grpc.health.v1`), vendored for the C++ currency service |

---

## `pb/demo.proto` — package `oteldemo`

`option go_package = "genproto/oteldemo";`

### Service definitions

#### CartService

```proto
service CartService {
    rpc AddItem(AddItemRequest) returns (Empty) {}
    rpc GetCart(GetCartRequest) returns (Cart) {}
    rpc EmptyCart(EmptyCartRequest) returns (Empty) {}
}
```

| Role | Service | Notes |
|------|---------|-------|
| Server | `src/cart` (.NET / C#) | Registered via `Grpc.AspNetCore`; proto included through `<Protobuf Include="$(ProtosDir)\**\*.proto" GrpcServices="Both" />` in `src/cart/src/cart.csproj` |
| Client | `src/checkout` (Go) | `pb.NewCartServiceClient(c)` in `src/checkout/main.go`; calls `GetCart` and `EmptyCart` over gRPC |
| Client | `src/frontend` (TypeScript) | `CartServiceClient` imported from `src/frontend/protos/demo.ts`; used in `src/frontend/gateways/rpc/Cart.gateway.ts` |

Key messages:

```proto
message CartItem        { string product_id = 1; int32 quantity = 2; }
message Cart            { string user_id = 1; repeated CartItem items = 2; }
message AddItemRequest  { string user_id = 1; CartItem item = 2; }
message GetCartRequest  { string user_id = 1; }
message EmptyCartRequest { string user_id = 1; }
```

---

#### RecommendationService

```proto
service RecommendationService {
  rpc ListRecommendations(ListRecommendationsRequest) returns (ListRecommendationsResponse){}
}
```

| Role | Service | Notes |
|------|---------|-------|
| Server | `src/recommendation` (Python) | `demo_pb2_grpc.add_RecommendationServiceServicer_to_server(service, server)` in `src/recommendation/recommendation_server.py` |
| Client | `src/frontend` (TypeScript) | `RecommendationServiceClient` in `src/frontend/gateways/rpc/Recommendations.gateway.ts` |

The recommendation server is also a **client** of `ProductCatalogService`: calls `ListProducts` / `GetProduct` via `demo_pb2_grpc.ProductCatalogServiceStub` (see `src/recommendation/recommendation_server.py` lines 84–95, 157–158).

Key messages:

```proto
message ListRecommendationsRequest  { string user_id = 1; repeated string product_ids = 2; }
message ListRecommendationsResponse { repeated string product_ids = 1; }
```

---

#### ProductCatalogService

```proto
service ProductCatalogService {
    rpc ListProducts(Empty) returns (ListProductsResponse) {}
    rpc GetProduct(GetProductRequest) returns (Product) {}
    rpc SearchProducts(SearchProductsRequest) returns (SearchProductsResponse) {}
}
```

| Role | Service | Notes |
|------|---------|-------|
| Server | `src/product-catalog` (Go) | `pb.RegisterProductCatalogServiceServer(srv, svc)` in `src/product-catalog/main.go` line 248 |
| Client | `src/checkout` (Go) | `pb.NewProductCatalogServiceClient(c)`; calls `GetProduct` per cart item (line 510) |
| Client | `src/recommendation` (Python) | `demo_pb2_grpc.ProductCatalogServiceStub(pc_channel)` in `src/recommendation/recommendation_server.py` line 158 |
| Client | `src/product-reviews` (Python) | `demo_pb2_grpc.ProductCatalogServiceStub(pc_channel)` in `src/product-reviews/product_reviews_server.py` line 377 |
| Client | `src/frontend` (TypeScript) | `ProductCatalogServiceClient` in `src/frontend/gateways/rpc/ProductCatalog.gateway.ts` |

Key messages:

```proto
message Product {
    string id = 1; string name = 2; string description = 3;
    string picture = 4; Money price_usd = 5; repeated string categories = 6;
}
message GetProductRequest      { string id = 1; }
message SearchProductsRequest  { string query = 1; }
message ListProductsResponse   { repeated Product products = 1; }
message SearchProductsResponse { repeated Product results = 1; }
```

---

#### ProductReviewService

```proto
service ProductReviewService {
  rpc GetProductReviews(GetProductReviewsRequest) returns (GetProductReviewsResponse){}
  rpc GetAverageProductReviewScore(GetAverageProductReviewScoreRequest) returns (GetAverageProductReviewScoreResponse){}
  rpc AskProductAIAssistant(AskProductAIAssistantRequest) returns (AskProductAIAssistantResponse){}
}
```

| Role | Service | Notes |
|------|---------|-------|
| Server | `src/product-reviews` (Python) | `demo_pb2_grpc.add_ProductReviewServiceServicer_to_server(service, server)` in `src/product-reviews/product_reviews_server.py` line 365 |
| Client | `src/frontend` (TypeScript) | `ProductReviewServiceClient` in `src/frontend/gateways/rpc/ProductReview.gateway.ts` |

Key messages:

```proto
message ProductReview { string username = 1; string description = 2; string score = 3; }
message GetProductReviewsRequest             { string product_id = 1; }
message GetProductReviewsResponse            { repeated ProductReview product_reviews = 1; }
message GetAverageProductReviewScoreRequest  { string product_id = 1; }
message GetAverageProductReviewScoreResponse { string average_score = 1; }
message AskProductAIAssistantRequest         { string product_id = 1; string question = 2; }
message AskProductAIAssistantResponse        { string response = 1; }
```

---

#### ShippingService

```proto
service ShippingService {
    rpc GetQuote(GetQuoteRequest) returns (GetQuoteResponse) {}
    rpc ShipOrder(ShipOrderRequest) returns (ShipOrderResponse) {}
}
```

| Role | Service | Notes |
|------|---------|-------|
| Server | `src/shipping` (Rust / Actix-web) | Exposes **HTTP** POST `/get-quote` and `/ship-order`. Does **not** use tonic or any gRPC runtime. Message shapes are hand-written Serde structs in `src/shipping/src/shipping_service/shipping_types.rs`. |
| Client | `src/checkout` (Go) | Calls shipping over **HTTP JSON** via `otelhttp.Post` to `/get-quote` (line 463) and `/ship-order` (line 583) in `src/checkout/main.go`. `pb.ShippingServiceClient` stub is allocated but never used to make calls. |

Key messages:

```proto
message GetQuoteRequest  { Address address = 1; repeated CartItem items = 2; }
message GetQuoteResponse { Money cost_usd = 1; }
message ShipOrderRequest  { Address address = 1; repeated CartItem items = 2; }
message ShipOrderResponse { string tracking_id = 1; }
```

> **Known inconsistency**: The proto defines gRPC RPCs but the Rust implementation uses HTTP. The `pb.ShippingServiceClient` in checkout is never used for actual RPC calls.

---

#### CurrencyService

```proto
service CurrencyService {
    rpc GetSupportedCurrencies(Empty) returns (GetSupportedCurrenciesResponse) {}
    rpc Convert(CurrencyConversionRequest) returns (Money) {}
}
```

| Role | Service | Notes |
|------|---------|-------|
| Server | `src/currency` (C++) | `class CurrencyService final : public oteldemo::CurrencyService::Service` in `src/currency/src/server.cpp` line 103; registered via `builder.RegisterService(&currencyService)` |
| Client | `src/checkout` (Go) | `pb.NewCurrencyServiceClient(c)`; calls `Convert` over gRPC |
| Client | `src/frontend` (TypeScript) | `CurrencyServiceClient` in `src/frontend/gateways/rpc/Currency.gateway.ts` |

Key messages:

```proto
message Money {
    string currency_code = 1; int64 units = 2; int32 nanos = 3;
}
message GetSupportedCurrenciesResponse { repeated string currency_codes = 1; }
message CurrencyConversionRequest      { Money from = 1; string to_code = 2; }
```

---

#### PaymentService

```proto
service PaymentService {
    rpc Charge(ChargeRequest) returns (ChargeResponse) {}
}
```

| Role | Service | Notes |
|------|---------|-------|
| Server | `src/payment` (Node.js) | `otelDemoPackage.oteldemo.PaymentService.service` added via `server.addService(...)` in `src/payment/index.js` line 45. Uses runtime `@grpc/proto-loader` — no compile-time code generation. |
| Client | `src/checkout` (Go) | `pb.NewPaymentServiceClient(c)`; calls `Charge` over gRPC (`src/checkout/main.go` line 543) |

Key messages:

```proto
message CreditCardInfo {
    string credit_card_number = 1; int32 credit_card_cvv = 2;
    int32 credit_card_expiration_year = 3; int32 credit_card_expiration_month = 4;
}
message ChargeRequest  { Money amount = 1; CreditCardInfo credit_card = 2; }
message ChargeResponse { string transaction_id = 1; }
```

---

#### EmailService

```proto
service EmailService {
    rpc SendOrderConfirmation(SendOrderConfirmationRequest) returns (Empty) {}
}
```

| Role | Service | Notes |
|------|---------|-------|
| Server | `src/email` (Ruby / Sinatra) | Exposes **HTTP** POST `/send_order_confirmation` in `src/email/email_server.rb` line 43. Does **not** use gRPC. |
| Client | `src/checkout` (Go) | Calls email over **HTTP JSON** via `otelhttp.Post` to `/send_order_confirmation` (`src/checkout/main.go` line 561). `pb.EmailServiceClient` stub is allocated but never used for RPC calls. |

Key messages:

```proto
message OrderItem { CartItem item = 1; Money cost = 2; }
message OrderResult {
    string order_id = 1; string shipping_tracking_id = 2;
    Money shipping_cost = 3; Address shipping_address = 4; repeated OrderItem items = 5;
}
message SendOrderConfirmationRequest { string email = 1; OrderResult order = 2; }
```

> **Known inconsistency**: The proto defines a gRPC method but the Ruby implementation is HTTP-only. Same pattern as ShippingService.

---

#### CheckoutService

```proto
service CheckoutService {
    rpc PlaceOrder(PlaceOrderRequest) returns (PlaceOrderResponse) {}
}
```

| Role | Service | Notes |
|------|---------|-------|
| Server | `src/checkout` (Go) | Implements `PlaceOrder`; orchestrates calls to cart, product-catalog, currency, payment (all gRPC), and shipping and email (both HTTP) |
| Client | `src/frontend` (TypeScript) | `CheckoutServiceClient` in `src/frontend/gateways/rpc/Checkout.gateway.ts` |

Key messages:

```proto
message PlaceOrderRequest {
    string user_id = 1; string user_currency = 2;
    Address address = 3; string email = 5; CreditCardInfo credit_card = 6;
}
message PlaceOrderResponse { OrderResult order = 1; }
```

---

#### AdService

```proto
service AdService {
    rpc GetAds(AdRequest) returns (AdResponse) {}
}
```

| Role | Service | Notes |
|------|---------|-------|
| Server | `src/ad` (Java) | `class AdServiceImpl extends oteldemo.AdServiceGrpc.AdServiceImplBase` in `src/ad/src/main/java/oteldemo/AdService.java`; stubs generated at build time by the Gradle `com.google.protobuf` plugin into `src/ad/build/generated/source/proto/main/{java,grpc}/oteldemo/` |
| Client | `src/frontend` (TypeScript) | `AdServiceClient` in `src/frontend/gateways/rpc/Ad.gateway.ts` |

Key messages:

```proto
message AdRequest  { repeated string context_keys = 1; }
message AdResponse { repeated Ad ads = 1; }
message Ad         { string redirect_url = 1; string text = 2; }
```

---

#### FeatureFlagService

```proto
service FeatureFlagService {
  rpc GetFlag(GetFlagRequest) returns (GetFlagResponse) {}
  rpc CreateFlag(CreateFlagRequest) returns (CreateFlagResponse) {}
  rpc UpdateFlag(UpdateFlagRequest) returns (UpdateFlagResponse) {}
  rpc ListFlags(ListFlagsRequest) returns (ListFlagsResponse) {}
  rpc DeleteFlag(DeleteFlagRequest) returns (DeleteFlagResponse) {}
}
```

| Role | Service | Notes |
|------|---------|-------|
| Server | **UNKNOWN / not implemented in this repo** | `FeatureFlagService` is defined in `pb/demo.proto` but no service implements it. Feature flags at runtime are managed by the third-party `flagd` binary via `src/flagd/demo.flagd.json`. The `flagd-ui` Elixir service reads/writes that JSON file directly — it does not call these RPCs. |
| Client | None found | No service in the repo calls any of these RPCs at runtime. The definition appears to be a historical artifact. |

Key messages:

```proto
message Flag             { string name = 1; string description = 2; bool enabled = 3; }
message GetFlagRequest   { string name = 1; }
message GetFlagResponse  { Flag flag = 1; }
message UpdateFlagRequest { string name = 1; bool enabled = 2; }
message ListFlagsResponse { repeated Flag flag = 1; }
message DeleteFlagRequest { string name = 1; }
```

---

### Shared common messages

These messages are referenced across multiple service contracts:

| Message | Used by |
|---------|---------|
| `Money` | CurrencyService, PaymentService, ShippingService, CheckoutService, OrderResult |
| `Address` | ShippingService, CheckoutService, OrderResult |
| `CartItem` | CartService, ShippingService, OrderResult |
| `OrderResult` | CheckoutService (`PlaceOrderResponse`), EmailService (`SendOrderConfirmationRequest`), Kafka `orders` topic |
| `OrderItem` | Nested inside `OrderResult` |
| `CreditCardInfo` | CheckoutService (`PlaceOrderRequest`), PaymentService (`ChargeRequest`) |
| `Empty` | CartService (returns), ProductCatalogService (arg/return), CurrencyService (arg), EmailService (return) |

---

## `src/currency/proto/grpc/health/v1/health.proto` — package `grpc.health.v1`

```proto
service Health {
  rpc Check(HealthCheckRequest) returns (HealthCheckResponse);
}
```

This is the canonical gRPC health-check proto vendored from `https://github.com/grpc/grpc-proto`. It is bundled locally because the C++ currency service builds using CMake and needs the proto source available. All other services use their language's gRPC health-check library at the binary level without vendoring this proto.

---

## Kafka — proto serialization outside gRPC

`OrderResult` (defined in `pb/demo.proto`) is also serialized as binary protobuf and published to the Kafka `orders` topic:

- **Producer**: `src/checkout` — `proto.Marshal(result)` in `src/checkout/main.go` (`sendToPostProcessor`, line 612)
- **Consumers**:
  - `src/fraud-detection` (Kotlin) — `OrderResult.parseFrom(record.value())` in `src/fraud-detection/src/main/kotlin/frauddetection/main.kt` line 64
  - `src/accounting` (.NET/C#) — `OrderResult.Parser.ParseFrom(message.Value)` in `src/accounting/Consumer.cs` line 90

The Kotlin fraud-detection service generates proto classes via the Gradle `com.google.protobuf` plugin. The .NET accounting service uses `<Protobuf Include="src\protos\demo.proto" GrpcServices="none" />` (message-only generation, no gRPC stubs) as declared in `src/accounting/Accounting.csproj`.

---

## Code generation approach

There is no `buf` toolchain in this repo. All generation uses `protoc` directly, invoked through one of two entry points.

### `make generate-protobuf` (local / IDE)

Invokes `./ide-gen-proto.sh`. The script uses a different protoc invocation per language:

| Language | Tool | Output location |
|----------|------|-----------------|
| Go | `protoc --go_out --go-grpc_out` | `src/{checkout,product-catalog}/genproto/oteldemo/` |
| Python | `python -m grpc_tools.protoc` | `src/{recommendation,product-reviews}/demo_pb2.py`, `demo_pb2_grpc.py` |
| TypeScript | `protoc-gen-ts_proto` (ts_proto npm package) | `src/{frontend,react-native-app}/protos/demo.ts` |
| .NET (cart) | MSBuild `<Protobuf GrpcServices="Both">` | Generated at MSBuild compile time; not committed |
| .NET (accounting) | MSBuild `<Protobuf GrpcServices="none">` | Messages only, generated at compile time; not committed |
| JavaScript (payment) | Runtime `@grpc/proto-loader` | No generated files; proto loaded at process startup |
| Rust (shipping) | No generation | Types are hand-written Serde structs in `src/shipping/src/shipping_service/shipping_types.rs` |
| Kotlin (fraud-detection) | Gradle `com.google.protobuf` plugin | Build-time into `build/generated/source/proto/`; not committed |
| Java (ad) | Gradle `com.google.protobuf` plugin | `src/ad/build/generated/source/proto/main/{java,grpc}/oteldemo/`; not committed |
| C++ (currency) | CMake + custom Docker build | `src/currency/build/generated/proto/` |

### `make docker-generate-protobuf`

Invokes `./docker-gen-proto.sh`. Builds a per-service Docker image from `src/<service>/genproto/Dockerfile`, runs `protoc` inside the container, and writes generated files back via a volume mount. Runs for: checkout, currency, frontend, product-catalog, product-reviews, recommendation.

### Inline `go:generate` directive

`src/checkout/main.go` line 63 documents the manual equivalent:

```
//go:generate protoc --go_out=./ --go-grpc_out=./ --proto_path=../../pb ../../pb/demo.proto
```

### `make clean` removes

```
src/{checkout,product-catalog}/genproto/oteldemo/
src/recommendation/{demo_pb2,demo_pb2_grpc}.py
src/frontend/protos/demo.ts
```

---

## Generated stub locations (committed files only)

| Service | Language | File(s) |
|---------|----------|---------|
| checkout | Go | `src/checkout/genproto/oteldemo/demo.pb.go`, `demo_grpc.pb.go` |
| product-catalog | Go | `src/product-catalog/genproto/oteldemo/demo.pb.go`, `demo_grpc.pb.go` |
| recommendation | Python | `src/recommendation/demo_pb2.py`, `src/recommendation/demo_pb2_grpc.py` |
| product-reviews | Python | `src/product-reviews/demo_pb2.py`, `src/product-reviews/demo_pb2_grpc.py` |
| frontend | TypeScript | `src/frontend/protos/demo.ts` |
| react-native-app | TypeScript | `src/react-native-app/protos/demo.ts` |
| currency | C++ | `src/currency/build/generated/proto/demo.pb.{cc,h}`, `demo.grpc.pb.{cc,h}`, `demo_mock.grpc.pb.h` |
| ad | Java | Build-time only — not committed |
| fraud-detection | Kotlin | Build-time only — not committed |
| cart | .NET | Compile-time only — not committed |
| accounting | .NET | Compile-time only, messages only — not committed |
| payment | Node.js | None — runtime proto-loader |
| shipping | Rust | None — hand-written structs |
