# UI Kit Detail

## Styling Token System

### How Tokens Are Delivered

Tokens are plain TypeScript object literals, not CSS custom properties. There is no generated CSS file and no design-token build step.

1. `src/frontend/styles/Theme.ts` exports a single `Theme` constant typed as `DefaultTheme`.
2. `src/frontend/styles/style.d.ts` extends the `styled-components` module to add the `DefaultTheme` interface.
3. `src/frontend/pages/_app.tsx` wraps the entire tree in `<ThemeProvider theme={Theme}>`.
4. Every styled-component can then access tokens via `${({ theme }) => theme.colors.otelBlue}`.

Because tokens are TypeScript values (not CSS variables), they cannot be inspected in DevTools computed styles, and overriding them at runtime requires re-rendering with a different theme object.

### Color Tokens with Hexes

```
theme.colors.otelBlue          #5262A8   primary CTA, badge fills, focus borders
theme.colors.otelYellow        #EAAA3B   ad banner, star ratings
theme.colors.otelGray          #403F4B   footer background
theme.colors.otelRed           #FB7181   destructive actions, cart badge
theme.colors.backgroundGray    rgba(64,63,75,0.1)   banner section tint
theme.colors.lightBorderGray   rgba(82,98,168,0.3)  score bar track
theme.colors.borderGray        #2E2437   input/select borders, card borders
theme.colors.textGray          #29293E   default body text (also set in globals.css)
theme.colors.textLightGray     #78788C   secondary/muted text
theme.colors.white             #FFFFFF   text-on-dark, card backgrounds
```

### Hardcoded Color Values Not in Theme

Several components use hardcoded hex literals that are not in the theme object. These are implicit tokens:

| Value | Location | Semantic Role |
|-------|----------|---------------|
| `#5262a8` | `Button/Button.tsx` | Duplicates `otelBlue` |
| `#853b5c` | `Header/Header.styled.ts` — `header` element bg | Unthemed magenta (never visible: header bg overridden by NavBar) |
| `#b4b2bb` | `Header/Header.styled.ts` — NavBar color | Muted nav text |
| `#f9f9f9` | `Input/Input.styled.ts` | Input/Select background |
| `#cacaca` | `Input/Input.styled.ts` | Input/Select border |
| `#605f64` | `CurrencySwitcher/CurrencySwitcher.styled.ts` | Muted container text |
| `rgba(0,112,201,0.15)` | `ProductReviews.styled.ts` — focus shadow | Focus ring color, different blue from otelBlue |

### Font Size Tokens — Mobile vs Desktop

The theme uses a `m`/`d` naming convention (mobile / desktop) rather than semantic names like `heading1`, `body`, etc.

```
Mobile:  mxLarge=22px  mLarge=20px  mMedium=14px  mSmall=12px
Desktop: dxLarge=58px  dLarge=40px  dMedium=18px  dSmall=16px  nano=8px
```

The `nano` token (8px) is exclusively used for the cart badge count (`CartIcon.styled.ts`).

### Single Breakpoint

Only one breakpoint exists: `theme.breakpoints.desktop = '@media (min-width: 768px)'`. The UI is mobile-first; desktop styles are applied inside this media query.

One exception: `Home.styled.ts` uses a raw `@media (max-width: 992px)` — this is inconsistent and bypasses the theme.

---

## Repeated UI Patterns

### 1. Chevron-Decorated Select

Three separate implementations of a `<select>` with an absolutely-positioned Chevron arrow:

- `Input` component, `type='select'` path — arrow at `top: 64px` (accounts for label height)
- `Select` component — arrow at `top: 20px` (no label)
- `CurrencySwitcher` — inline select with `Chevron.svg` at `right: 15px`

All three use `src='/icons/Chevron.svg'` via `styled.img.attrs(...)`. The positioning values differ because each evolved independently.

### 2. Button Extension Pattern

`Button` is a styled-component, and several other files extend it with `styled(Button)` to apply layout-specific overrides:

- `Banner.styled.ts` — `GoShoppingButton` adds full-width mobile, auto desktop
- `CheckoutForm.styled.ts` — `CartButton` adds padding and width overrides
- `CheckoutForm.styled.ts` — `EmptyCartButton` adds red text and full-width
- `Cart.styled.ts` — `EmptyCartButton` (duplicate name, different file) adds red text
- `ProductDetail.styled.ts` — `AddToCart` adds flex centering and specific width

### 3. Product Image via CSS background-image

`ProductCard.styled.ts` and `ProductDetail.styled.ts` both render product images as `background-image` on a sized `<div>`, not as `<img>` tags. This pattern means no `alt` text is present. Both use `background-size: contain`.

### 4. Section with Title Pattern

Multiple sections repeat the same structure: a wrapper, a `TitleContainer` with a decorative top border, and a `Title`. Examples: `ProductReviews`, `Recommendations`.

### 5. Responsive Container with 20px/100px Padding

Most page-level containers use `padding: 0 20px` on mobile and `padding: 0 100px` on desktop. This pattern appears in `Home.styled.ts`, `Header.styled.ts`, and `ProductDetail.styled.ts` but is not extracted into a shared component or mixin.

### 6. data-cy Attributes for E2E Testing

Nearly every interactive or data-showing element carries `data-cy` attributes mapped to `src/frontend/utils/enums/CypressFields.ts`. The enum is the single source of truth for Cypress test selectors.

---

## Provider Architecture

State that feeds components comes from React context providers, not component props:

| Provider | Context | Used By |
|----------|---------|---------|
| `CartProvider` | `src/frontend/providers/Cart.provider.tsx` | CartIcon, CartItems, CartDetail |
| `CurrencyProvider` | `src/frontend/providers/Currency.provider.tsx` | CurrencySwitcher, ProductPrice, CartItems |
| `AdProvider` | `src/frontend/providers/Ad.provider.tsx` | Ad, Recommendations |
| `ProductReviewProvider` | `src/frontend/providers/ProductReview.provider.tsx` | ProductReviews |
| `ProductAIAssistantProvider` | `src/frontend/providers/ProductAIAssistant.provider.tsx` | ProductReviews |

All providers are composed in `_app.tsx`. Components that depend on a provider cannot be rendered outside that provider tree without error.

---

## Accessibility State

| Component | Issues |
|-----------|--------|
| `Input` | Label is `<p>`, not `<label for="id">`. Input and label not programmatically linked. |
| `Button` | No `aria-disabled` when used in disabled states. |
| `CartDropdown` | `Close` is a `<span onClick>`. No `role="dialog"`, no focus trap, no `aria-modal`. |
| `ProductCard` | Product image rendered as CSS background-image — no `alt` attribute possible. |
| `ProductReviews` | Best ARIA usage: `aria-live`, `aria-busy`, `aria-label` on inputs, `role="alert"` on errors. |
| `CheckoutItem` | `<span>Done</span>` next to Check.svg icon — icon has `alt="check"` via Next `<Image>`, acceptable. |
| `CurrencySwitcher` | Select has no `aria-label` or `<label>`. |

---

## Feature Flag Integration

`ProductCard` uses `@openfeature/react-sdk` to read the `imageSlowLoad` flag (number). When non-zero, it appends `x-envoy-fault-delay-request: <value>` to the image fetch request. This is the only component-level feature flag usage. The flag system is initialized in `_app.tsx` via `FlagdWebProvider`.

