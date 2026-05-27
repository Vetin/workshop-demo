# TypeScript / Next.js Language Knowledge

Services: `src/frontend/`

## Version and Toolchain

- Node.js 20+
- TypeScript 5+
- Next.js 14 (**Pages Router — NOT App Router**)
- React 18
- styled-components v6
- TanStack Query v5 (`@tanstack/react-query`)
- OpenFeature (`@openfeature/react-sdk`, `@openfeature/web-sdk`)

## Commands

| Task | Command | Working Directory |
|---|---|---|
| Install deps | `npm install` | `src/frontend/` |
| Dev server | `npm run dev` | `src/frontend/` |
| Production build | `npm run build` | `src/frontend/` |
| Test | `npm test` or `npx playwright test` | `src/frontend/` |
| Lint | `npm run lint` | `src/frontend/` |

## Next.js Architecture

**Pages Router only.** All routes live under `src/frontend/pages/`.

| Pattern | Correct |
|---|---|
| Data fetching | `getServerSideProps` for SSR, `getStaticProps` for static |
| API routes | `pages/api/` — thin BFF proxies to backend gRPC services |
| Routing | File-based pages router |
| Layout | `_app.tsx` / `_document.tsx` |

Do **not** introduce App Router patterns (`app/` directory, `use client`,
`use server`, Server Components, or `fetch()` with `cache:` options) — the
project uses Pages Router throughout.

## OpenTelemetry Instrumentation

Dual-environment setup:

| Environment | Mechanism |
|---|---|
| SSR / Node.js | `@opentelemetry/auto-instrumentations-node` in `instrumentation.ts` |
| Browser | OTLP HTTP trace export via `@opentelemetry/exporter-trace-otlp-http` |

`instrumentation.ts` (Next.js instrumentation hook) initializes the Node.js
SDK for the server side. The browser SDK is initialized in a client-side
module loaded by `_app.tsx`.

**Never initialize the SDK twice** — Next.js hot reload can trigger the
`instrumentation.ts` hook multiple times; guard with a singleton check.

`traceparent` header must flow from SSR page to browser — verify it is not
stripped by the Envoy frontend-proxy config (`src/frontend-proxy/envoy.tmpl.yaml`).

## Generated Proto Stubs

`src/frontend/protos/demo.ts` — do not hand-edit.

Regenerate with:
```
make docker-generate-protobuf
```

## Styling — styled-components v6

- Use theme tokens via `props.theme.*` — never hardcode color hex values or
  pixel sizes.
- Theme is provided at app root via `ThemeProvider`.
- v6 syntax: use `styled.div` etc. directly; dynamic styles via template
  literal interpolation.

## Feature Flags — OpenFeature

Flags are defined in `src/flagd/demo.flagd.json`. Access in components:

```tsx
import { useFlag } from '@openfeature/react-sdk';

const { value: featureEnabled } = useFlag('myFeatureFlagKey', false);
```

Flag key strings must exactly match keys in `demo.flagd.json`. A mismatch
silently returns the default value — no runtime error.

## Key TypeScript Idioms

- Avoid `any` — use `unknown` + type guards, or generate proper types.
- Null-check before accessing optional properties:
  ```ts
  const name = product?.name ?? 'Unknown';
  ```
- API route handlers must handle errors and return correct HTTP status codes:
  ```ts
  res.status(500).json({ error: err.message });
  ```
- Use `GetServerSidePropsContext` / `NextApiRequest` types, not bare `any`.

## Common Failure Modes

| Symptom | Root Cause |
|---|---|
| App Router errors at build | App Router patterns (`app/` dir, Server Components) mixed with Pages Router |
| Hardcoded colors not matching theme | Colors not from `props.theme.*` |
| Feature flag always returns default | Flag key typo; does not match key in `demo.flagd.json` |
| Missing traces on browser navigation | `traceparent` header stripped by Envoy proxy |
| Double OTel init on hot reload | `instrumentation.ts` not guarded with singleton check |
| Proto type errors | `demo.ts` stale after `pb/demo.proto` change — regenerate |

## Implementer Rules

1. Never use the App Router — all new routes go under `pages/`.
2. Do not hardcode design tokens — use `props.theme.*`.
3. Validate flag keys against `src/flagd/demo.flagd.json` before committing.
4. Do not hand-edit `src/frontend/protos/demo.ts`.
5. Protect OTel SDK init against double-initialization on hot reload.

## Reviewer Checks

- `any` types in new code — require proper typing.
- Missing null checks on optional fields from API responses.
- Double OTel SDK init path (instrumentation.ts without singleton guard).
- PII (user email, address, payment info) added to span attributes.
- Hardcoded colors or pixel values outside theme.
- App Router imports (`next/navigation`, `use client`, `use server`).
- Flag key string that does not appear in `demo.flagd.json`.
