# UI Kit Overview

## Technology Stack

The frontend (`src/frontend/`) is a **Next.js 16** application using **React 19**. There is no third-party component library (no Material UI, Chakra, Ant Design, etc.). All UI is hand-rolled using **styled-components v6** as the sole styling engine.

- **Framework**: Next.js 16 (Pages Router)
- **Component library**: None — all components are bespoke
- **Styling engine**: styled-components v6 (`src/frontend/package.json`)
- **Theme system**: custom `DefaultTheme` declared in `src/frontend/styles/style.d.ts`, instantiated in `src/frontend/styles/Theme.ts`, injected app-wide via `<ThemeProvider>` in `src/frontend/pages/_app.tsx`
- **Global CSS**: `src/frontend/styles/globals.css` (resets, body font, flex shell)
- **Font**: Google Fonts — Open Sans (weights 300–800, loaded in `src/frontend/pages/_document.tsx`)
- **Icon library**: None. Four hand-crafted SVG files live in `src/frontend/public/icons/`: `Cart.svg`, `CartIcon.svg`, `Check.svg`, `Chevron.svg`
- **Storybook**: Not present
- **Component docs**: Not present

## Directory Layout

```
src/frontend/
├── components/          # 21 feature/UI component folders, each owning *.tsx + *.styled.ts + index.ts
├── styles/
│   ├── Theme.ts         # Token values (colors, sizes, fonts, breakpoints)
│   ├── style.d.ts       # TypeScript module augmentation for DefaultTheme
│   ├── globals.css      # Base resets
│   ├── Cart.styled.ts   # Page-level styled components for /cart
│   ├── Checkout.styled.ts
│   ├── Home.styled.ts
│   └── ProductDetail.styled.ts
├── pages/               # Next.js page files (_app.tsx injects ThemeProvider)
└── public/icons/        # SVG icons (4 files)
```

## Styling Architecture

Every component follows the same co-location pattern:

```
ComponentName/
  ComponentName.tsx        # Logic and JSX
  ComponentName.styled.ts  # All styled-components for this component
  index.ts                 # Re-export default
```

Inside styled files, local styled primitives are imported as `* as S` and used as `<S.Foo>`. This keeps styled-component names out of the global namespace and makes the separation of concerns explicit.

Page-level layout styled components that span multiple components live directly in `src/frontend/styles/` (e.g., `Cart.styled.ts`, `Home.styled.ts`, `ProductDetail.styled.ts`).

## Theme Tokens

All design tokens are TypeScript values (not CSS custom properties). They are accessed via `${({ theme }) => theme.<category>.<token>}` inside styled-component template literals.

**Colors** (9 named):
- `otelBlue` #5262A8 — primary action, badges, focus rings
- `otelYellow` #EAAA3B — ad banner background, star ratings
- `otelGray` #403F4B — footer background, body text in AI panel
- `otelRed` #FB7181 — destructive actions (empty cart), cart badge
- `backgroundGray` rgba(64,63,75,0.1) — banner section background
- `lightBorderGray` rgba(82,98,168,0.3) — score bar track
- `borderGray` #2E2437 — borders, select outlines
- `textGray` #29293E — default body text
- `textLightGray` #78788C — secondary/muted text

**Font weights** (mapped as named values):
- `bold` 800, `semiBold` 700, `regular` 500, `light` 400

**Font sizes** — two scales, mobile (`m`) and desktop (`d`):

| Token    | Value | Usage |
|----------|-------|-------|
| mxLarge  | 22px  | mobile hero title |
| mLarge   | 20px  | mobile section titles |
| mMedium  | 14px  | mobile body |
| mSmall   | 12px  | mobile small |
| dxLarge  | 58px  | desktop hero title |
| dLarge   | 40px  | desktop section titles |
| dMedium  | 18px  | desktop body / input labels |
| dSmall   | 16px  | desktop small / product names |
| nano     | 8px   | cart badge count |

**Breakpoints**:
- `desktop` `@media (min-width: 768px)` — single breakpoint, mobile-first

## Reusable Components (21 total)

See `docs/ai-knowledge/ui-kit/component-inventory.md` for detailed prop signatures and notes.

**Primitive / form controls** (stateless, broad reuse):
- `Button` — styled-component-only, three variants: `primary`, `secondary`, `link`
- `Input` — wraps `<input>` or `<select>` with label + chevron decoration
- `Select` — standalone select with chevron, used only in header currency switcher

**Domain atoms** (stateless display, tied to domain types):
- `ProductPrice` — formats a `Money` protobuf value with currency symbol

**Domain molecules** (stateful or composed):
- `ProductCard` — product thumbnail, fetches image with feature-flag delay header
- `ProductList` — grid wrapper that renders a list of `ProductCard`
- `CartIcon` — header icon with badge count; owns dropdown state
- `CartDropdown` — overlay panel triggered by `CartIcon`
- `CartItems` — table of cart rows with shipping/total calculation
- `CheckoutItem` — single order confirmation row with collapsible address
- `CheckoutForm` — full shipping + payment form (manages own controlled-input state)
- `CurrencySwitcher` — select in the header to change active currency
- `Recommendations` — "You May Also Like" strip using `ProductCard`
- `ProductReviews` — reviews summary + AI Ask panel (stateful)
- `Banner` — marketing hero section (static)
- `Ad` — displays one random ad from provider
- `PlatformFlag` — displays deployment platform string in footer

**Layout / structural**:
- `Layout` — composes `Header + <main> + Footer` shell for every page
- `Header` — top navigation bar (logo, CurrencySwitcher, CartIcon)
- `Footer` — bottom bar with session ID and platform info

## No Storybook, No Design System Package

There is no Storybook, no Chromatic, no component documentation site, and no published npm package. The entire UI is self-contained within `src/frontend/`. See `docs/ai-knowledge/ui-kit/gaps.md` for Code Connect readiness assessment.
