# Node.js (JavaScript) Language Knowledge

Services: `src/payment/`

Note: payment is **JavaScript, not TypeScript**. There is no compilation step.
Do not introduce TypeScript without an explicit spec change.

## Version and Toolchain

- Node.js 20+
- npm for package management

## Commands

| Task | Command | Working Directory |
|---|---|---|
| Install deps | `npm install` | `src/payment/` |
| Run | `node index.js` (or entry defined in `package.json`) | `src/payment/` |
| Test | `npm test` | `src/payment/` (if configured) |
| Lint | `npm run lint` or `npx eslint .` | `src/payment/` |

## OpenTelemetry Instrumentation

Uses `@opentelemetry/auto-instrumentations-node` registered at process startup
before any other imports. The registration must happen before any other
`require`/`import` calls so the monkey-patching intercepts the grpc library:

```js
// Must be first in the entry module
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
// ... configure and start sdk before other requires
```

OTLP gRPC exporter endpoint configured via `OTEL_EXPORTER_OTLP_ENDPOINT`.

## Proto Loading

payment uses `@grpc/proto-loader` to load `pb/demo.proto` at module load time
(not per-request). The proto file path is resolved relative to `__dirname`:

```js
const PROTO_PATH = path.join(__dirname, '../../pb/demo.proto');
const packageDefinition = protoLoader.loadSync(PROTO_PATH, { ... });
```

Key rules:
- Load once at module level, not inside request handlers.
- Path is relative to the service file's location — verify it after any
  directory restructuring.
- If `pb/demo.proto` changes, the service must be restarted (no hot reload of
  proto definitions).

## Key JavaScript Idioms

- `async`/`await` for all asynchronous operations — no callback-style code
  in new features.
- Wrap all `await` calls in `try/catch`:
  ```js
  try {
      const result = await someAsyncOp();
  } catch (err) {
      span.recordException(err);
      throw err;
  }
  ```
- Validate required `process.env.*` variables at startup and fail fast with a
  clear error message if they are missing.
- Never use `var` — use `const` by default, `let` when reassignment is needed.

## Common Failure Modes

| Symptom | Root Cause |
|---|---|
| `Error: Cannot find module` for proto | Proto file path breaks when service is run from a different CWD; use `__dirname`-relative path |
| `span.end()` not called on error path | Missing `span.end()` in `catch` block; use `try/finally` |
| OTel SDK not active | `require('@opentelemetry/...')` not first in entry module; another module imported before SDK init |
| gRPC `UNIMPLEMENTED` error | Proto definition mismatch — proto file updated but service not restarted |
| Secrets in logs | `console.log(process.env.PAYMENT_API_KEY)` or similar — never log env vars |

## Implementer Rules

1. OTel SDK registration must be the first code executed in the entry module.
2. Load proto definitions once at module level — never inside a handler.
3. Always call `span.end()` in a `finally` block so it is never missed.
4. Validate all required `process.env.*` at startup.
5. Do not introduce TypeScript without an explicit spec change.

## Reviewer Checks

- Proto loaded inside a request handler (performance and correctness issue).
- `console.log` used for diagnostics in production paths (use structured logging
  or OTel log bridge).
- OTel SDK initialized after other module imports.
- Missing `span.end()` in error paths.
- `var` keyword used.
- `process.env.*` access without existence check at startup.
