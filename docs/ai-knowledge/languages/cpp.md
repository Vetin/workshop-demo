# C++ Language Knowledge

Services: `src/currency/`

## Version and Toolchain

- C++17 standard
- CMake build system
- Compiler: GCC or Clang (as used in the Dockerfile base image)

## Commands

| Task | Command | Notes |
|---|---|---|
| Configure | `cmake -B build .` | From `src/currency/` |
| Build | `cmake --build build` | From `src/currency/` |
| Test | `ctest --test-dir build` | From build directory |
| Lint | `clang-tidy -p build src/*.cc` | If `compile_commands.json` generated |
| Clean | `rm -rf build/` | Clears CMake cache |

In the Dockerfile the build typically runs as:

```dockerfile
RUN cmake -DCMAKE_BUILD_TYPE=Release .. && make -j$(nproc)
```

from the `build/` subdirectory. Match this pattern when running locally.

## OpenTelemetry Instrumentation

Uses the OpenTelemetry C++ SDK (`opentelemetry-cpp`) with OTLP gRPC exporter.

Tracer acquisition:

```cpp
#include "opentelemetry/trace/provider.h"
namespace trace = opentelemetry::trace;

auto provider = opentelemetry::trace::Provider::GetTracerProvider();
auto tracer   = provider->GetTracer("currency", "1.0.0");
```

Span lifecycle:

```cpp
auto span = tracer->StartSpan("Convert");
auto scope = opentelemetry::trace::Scope(tracer->WithActiveSpan(span));
// ... work ...
span->SetStatus(trace::StatusCode::kOk);
span->End();
```

On error:

```cpp
span->SetStatus(trace::StatusCode::kError, err.message());
span->End();
```

OTLP gRPC exporter is configured at startup; endpoint from
`OTEL_EXPORTER_OTLP_ENDPOINT`.

## Generated Proto Stubs

Location: `src/currency/build/generated/proto/` (created during `cmake` build).

**Do not hand-edit these files.** After changing `pb/demo.proto`:
1. Run `make docker-generate-protobuf` to regenerate stubs for all languages.
2. Re-run the cmake build to pick up the new generated headers.

## Key C++ Idioms

- RAII for resource management — all resources (file handles, network connections,
  gRPC channels) must be owned by a class and released in its destructor.
- Smart pointers only:
  - `std::unique_ptr<T>` for sole-ownership resources
  - `std::shared_ptr<T>` for shared ownership
  - No raw `new`/`delete` in application code
- Prefer `std::string_view` over `const std::string&` for read-only string
  parameters.
- Use `[[nodiscard]]` on functions returning error codes or status objects.
- Structured error handling via return values or exceptions — no `abort()` in
  request handlers.

## Common Failure Modes

| Symptom | Root Cause |
|---|---|
| Compile error after proto change | Generated headers in `build/generated/` are stale — delete `build/` and rebuild |
| CMake cache error | Old `CMakeCache.txt` after a dependency change — delete `build/` and reconfigure |
| Linker error `undefined reference to opentelemetry::...` | CMake not finding `opentelemetry-cpp` — check `find_package(opentelemetry-cpp)` in `CMakeLists.txt` |
| Spans not emitted | `OTEL_EXPORTER_OTLP_ENDPOINT` not set or OTel provider not initialized before first span |
| Segfault in gRPC handler | Raw pointer used after free; replace with `shared_ptr` |

## Implementer Rules

1. Never use raw `new`/`delete` — always use smart pointers.
2. Always call `span->End()` in every code path including error returns.
3. Do not hand-edit generated proto headers in `build/generated/`.
4. After changing `pb/demo.proto`, delete the cmake build directory and
   rebuild from scratch to avoid stale generated code.
5. Map gRPC status codes to span status: `grpc::StatusCode::OK` →
   `trace::StatusCode::kOk`, others → `trace::StatusCode::kError`.

## Reviewer Checks

- Raw pointers (`T*`) used for ownership (not just observation).
- `new` / `delete` in application code.
- `span->End()` missing on any return path.
- gRPC error codes not reflected in span status.
- CMake minimum version lowered below C++17 requirement.
- `build/generated/` files hand-edited.
