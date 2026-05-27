# Component Inventory

All components live under `src/frontend/components/<Name>/`. Each folder exports a default from `index.ts`.

---

## Button

**File**: `src/frontend/components/Button/Button.tsx`

A styled-component directly (no wrapper function). Extends `styled.button`.

**Props**:
| Prop | Type | Default | Notes |
|------|------|---------|-------|
| `$type` | `'primary' \| 'secondary' \| 'link'` | `'primary'` | Transient prop ($ prefix, not forwarded to DOM) |
| All native `<button>` HTML attributes | — | — | Passed through |

**Variants**:
- `primary`: otelBlue background, white text, 1px otelBlue border, border-radius 10px, height 62px
- `secondary`: transparent background, otelBlue text, border retained
- `link`: transparent background, otelBlue text, no border

**Usage pattern**: Button is frequently extended with `styled(Button)` in other components (`Banner.styled.ts`, `CheckoutForm.styled.ts`, `Cart.styled.ts`, `ProductDetail.styled.ts`) to apply layout overrides while keeping the base variant behavior.

**Accessibility gap**: No `aria-label` or `aria-disabled` applied by default. Callers must provide accessible labels for icon-only usages.

---

## Input

**File**: `src/frontend/components/Input/Input.tsx`

Renders either a labeled `<input>` or a labeled `<select>` with a Chevron arrow decoration. Merges `type='select'` as a custom type extension.

**Props**:
| Prop | Type | Required | Notes |
|------|------|----------|-------|
| `type` | `HTMLInputTypeAttribute \| 'select'` | Yes | `'select'` switches to `<select>` render path |
| `label` | `string` | Yes | Rendered as `<p>` above the control |
| `id` | `string` | No | Forwarded to the inner element |
| `children` | `React.ReactNode` | No | `<option>` elements when `type='select'` |
| All `InputHTMLAttributes` | — | No | Spread onto inner element |

**Sub-elements** (from `Input.styled.ts`):
- `InputRow` — relative-positioned container, `margin-bottom: 24px`
- `InputLabel` — `dMedium` font size, `semiBold` weight
- `Input` — `border-radius: 10px`, background `#f9f9f9`, `border: 1px solid #cacaca`
- `Select` — same border style as Input
- `Arrow` — `<img>` using `Chevron.svg`, absolutely positioned at `right: 20px, top: 64px`

**Known issue**: Arrow top offset (64px) is hardcoded and assumes a fixed label height. If the label wraps, the chevron misaligns.

**Accessibility gap**: No `<label for=...>` element. The label is a `<p>` tag, not a `<label>`, so the control and its label are not programmatically associated. Screen readers will not announce the label when the control is focused.

---

## Select

**File**: `src/frontend/components/Select/Select.tsx`

Standalone select widget with Chevron icon. Separate from `Input type='select'` — used only inside `CurrencySwitcher`.

**Props**:
| Prop | Type | Required | Notes |
|------|------|----------|-------|
| `children` | `React.ReactNode` | Yes | `<option>` elements |
| All `InputHTMLAttributes<HTMLSelectElement>` | — | No | Spread onto `<select>` |

**Note**: `Select.styled.ts` and `Input.styled.ts` both define a `Select` styled component with different border and sizing values — they are not the same element and are not shared.

---

## ProductPrice

**File**: `src/frontend/components/ProductPrice/ProductPrice.tsx`

Renders a currency symbol + formatted decimal amount. Reads active currency from `CurrencyProvider`.

**Props**:
| Prop | Type | Required | Notes |
|------|------|----------|-------|
| `price` | `Money` (protobuf) | Yes | `{ units: number, nanos: number, currencyCode: string }` |

**Output**: `<span data-cy="ProductPrice">$ 12.99</span>`

**Behavior**: Uses `currency-symbol-map` to convert `currencyCode` to symbol. Falls back to `selectedCurrency` string if symbol not found. Computes total as `units + nanos / 1e9`.

---

## ProductCard

**File**: `src/frontend/components/ProductCard/ProductCard.tsx`

Displays product thumbnail, name, and price as a clickable card linking to `/product/[id]`.

**Props**:
| Prop | Type | Required | Notes |
|------|------|----------|-------|
| `product` | `Product` (protobuf) | Yes | Destructures `id`, `picture`, `name`, `priceUsd` |

**Behavior**: Fetches the product image via `fetch()` with a custom header `x-envoy-fault-delay-request` set from the `imageSlowLoad` OpenFeature flag value. Image is loaded as an object URL, not a Next.js `<Image>`. The image div uses a CSS background-image with `background-size: contain`.

**Accessibility gap**: The background-image approach means there is no `alt` text on the product image.

---

## ProductList

**File**: `src/frontend/components/ProductList/ProductList.tsx`

Renders a responsive CSS Grid of `ProductCard` components. 1 column on mobile, 3 columns on desktop.

**Props**:
| Prop | Type | Required | Notes |
|------|------|----------|-------|
| `productList` | `Product[]` | Yes | — |

---

## CartIcon

**File**: `src/frontend/components/CartIcon/CartIcon.tsx`

Header icon that shows a badge count when items are in cart. Controls `CartDropdown` open state.

No props. Reads `cart.items` from `CartProvider`.

**Sub-components rendered**: `CartDropdown`

---

## CartDropdown

**File**: `src/frontend/components/CartDropdown/CartDropdown.tsx`

Overlay panel listing cart items with a CTA to the full cart page. Closes on outside click.

**Props**:
| Prop | Type | Required | Notes |
|------|------|----------|-------|
| `isOpen` | `boolean` | Yes | Controls render (null if false) |
| `onClose` | `() => void` | Yes | Called on outside click or Close span click |
| `productList` | `IProductCartItem[]` | Yes | Cart items to display |

**Accessibility gap**: "Close" is a plain `<span onClick>`. Should be a `<button>`. No `role="dialog"`, no focus trap, no `aria-modal`.

---

## CartItems

**File**: `src/frontend/components/CartItems/CartItems.tsx`

Full cart table with product rows, shipping cost (fetched via `@tanstack/react-query`), and total.

**Props**:
| Prop | Type | Required | Notes |
|------|------|----------|-------|
| `productList` | `IProductCartItem[]` | Yes | — |
| `shouldShowPrice` | `boolean` | No (default `true`) | Hides shipping/total rows when false |

**Sub-components**: Renders `CartItem` (internal) and `ProductPrice`.

---

## CheckoutItem

**File**: `src/frontend/components/CheckoutItem/CheckoutItem.tsx`

Single row in the order confirmation page showing item details and collapsible shipping address.

**Props**:
| Prop | Type | Required | Notes |
|------|------|----------|-------|
| `checkoutItem` | `IProductCheckoutItem` | Yes | Item + cost |
| `address` | `Address` (protobuf) | Yes | Shipping address |

---

## CheckoutForm

**File**: `src/frontend/components/CheckoutForm/CheckoutForm.tsx`

Full controlled form for shipping address and credit card payment. Manages all field state internally.

**Props**:
| Prop | Type | Required | Notes |
|------|------|----------|-------|
| `onSubmit` | `(formData: IFormData) => void` | Yes | Called with typed form data on submit |

**IFormData** fields: `email`, `streetAddress`, `city`, `state`, `country`, `zipCode`, `creditCardNumber`, `creditCardCvv`, `creditCardExpirationYear`, `creditCardExpirationMonth`.

**Pre-filled defaults**: form ships with Mountain View CA address and a test Visa number.

**Accessibility gap**: Uses `Input` component throughout, which has the `<p>` label issue described above.

---

## CurrencySwitcher

**File**: `src/frontend/components/CurrencySwitcher/CurrencySwitcher.tsx`

Select dropdown in the header showing the active currency symbol and allowing the user to switch.

No props. Reads/writes from `CurrencyProvider`.

---

## Recommendations

**File**: `src/frontend/components/Recommendations/Recommendations.tsx`

"You May Also Like" section rendering a horizontal strip of `ProductCard` components.

No props. Reads `recommendedProductList` from `AdProvider`.

---

## ProductReviews

**File**: `src/frontend/components/ProductReviews/ProductReviews.tsx`

Complex component combining:
1. AI Assistant panel (`AskAISection`) — text input, three quick-prompt chips, response display
2. Rating summary card — average score badge, star rating, score distribution bar chart
3. Reviews grid — 1 column mobile, 5 columns desktop

No props. Reads from `ProductReviewProvider` and `ProductAIAssistantProvider`.

**Internal sub-component**: `StarRating` (local function, not exported) renders Unicode star characters `★ ☆` with `aria-label`.

**Accessibility**: `aria-live="polite"` on the section and on the AI response paragraph. `aria-busy` on the Ask button. `aria-label` on the AI input field. This component has the most complete ARIA usage in the codebase.

---

## Banner

**File**: `src/frontend/components/Banner/Banner.tsx`

Static marketing hero. No props. Renders hardcoded headline "The best telescopes to see the world closer" and a "Go Shopping" CTA linking to `#hot-products`.

---

## Ad

**File**: `src/frontend/components/Ad/Ad.tsx`

Displays a randomly selected ad from `AdProvider`. Yellow background strip with a link.

No props. Reads `adList` from `useAd()`.

**Behavior**: Random selection on every render (no memoization).

---

## PlatformFlag

**File**: `src/frontend/components/PlatformFlag/PlatformFlag.tsx`

Displays `window.ENV.NEXT_PUBLIC_PLATFORM` string in the footer. No props. Falls back to `'local'`.

---

## Cart/CartDetail

**File**: `src/frontend/components/Cart/CartDetail.tsx`

Assembles the full `/cart` page body: `CartItems` + `CheckoutForm` side by side. Handles order placement and redirects to confirmation.

No props. Reads from `CartProvider`, `CurrencyProvider`. Uses `SessionGateway`.

---

## Cart/EmptyCart

**File**: `src/frontend/components/Cart/EmptyCart.tsx`

Displayed when the cart is empty. No props reviewed (file exists, content not read in detail — likely static illustration/message).

---

## Layout

**File**: `src/frontend/components/Layout/Layout.tsx`

Thin shell: `Header` + `<main>{children}</main>` + `Footer`.

**Props**:
| Prop | Type | Required |
|------|------|----------|
| `children` | `React.ReactNode` | Yes |

---

## Header

**File**: `src/frontend/components/Header/Header.tsx`

Top navigation bar. No props. Contains logo (`<img>` to `/images/opentelemetry-demo-logo.png`), `CurrencySwitcher`, `CartIcon`.

**Dimensions**: 80px mobile, 100px desktop.

---

## Footer

**File**: `src/frontend/components/Footer/Footer.tsx`

Bottom bar showing demo disclaimer, session ID (hydrated client-side), copyright, and `PlatformFlag`. No props.

