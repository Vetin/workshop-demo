# Figma Mapping and Code Connect Readiness

## Summary

No Figma file, no Storybook, and no Code Connect configuration currently exist. This document captures the candidate Figma component mappings and the gaps that must be closed before Figma Code Connect (or any design-to-code bridge) is practical.

---

## Candidate Figma Component Mappings

The table below maps each React component to the probable Figma frame/component type it would correspond to in a standard design file.

| React Component | Figma Component Candidate | Variant Properties to Map |
|----------------|--------------------------|---------------------------|
| `Button` | Button | `type` → Figma variant: Primary / Secondary / Link |
| `Input` | Text Field | `type` → Input / Select; `label` → label layer |
| `Select` | Dropdown | — |
| `ProductPrice` | Price Label | — (display-only, no variants) |
| `ProductCard` | Product Card | — |
| `ProductList` | Product Grid | — (layout frame, not a component) |
| `CartIcon` | Cart Icon Button | badge count: shown/hidden |
| `CartDropdown` | Cart Drawer / Popover | open/closed state |
| `CartItems` | Cart Table | `shouldShowPrice` → show/hide totals |
| `CartItem` | Cart Row | — |
| `CheckoutItem` | Order Line Item | collapsed/expanded state |
| `CheckoutForm` | Checkout Form | — (form, not a variant-bearing component) |
| `CurrencySwitcher` | Currency Select | — |
| `Recommendations` | Recommendation Strip | empty/populated state |
| `ProductReviews` | Reviews Section | loading/loaded/empty states; AI panel open/answered |
| `Banner` | Hero Banner | static, no variants |
| `Ad` | Ad Banner | static, no variants |
| `PlatformFlag` | Platform Badge | — |
| `Layout` | Page Frame | not a component in Figma, a layout frame |
| `Header` | Navigation Bar | — |
| `Footer` | Footer Bar | — |

---

## Token Mapping — Theme to Figma Variables

If a Figma Variables collection is created to match the theme, these are the mappings:

**Colors collection**:
```
otelBlue          → Primary/Blue        #5262A8
otelYellow        → Accent/Yellow       #EAAA3B
otelGray          → Neutral/Dark        #403F4B
otelRed           → Feedback/Error      #FB7181
backgroundGray    → Surface/Subtle      rgba(64,63,75,0.1)
lightBorderGray   → Border/Light        rgba(82,98,168,0.3)
borderGray        → Border/Default      #2E2437
textGray          → Text/Primary        #29293E
textLightGray     → Text/Secondary      #78788C
white             → Text/OnDark         #FFFFFF
```

**Hardcoded values that need to be added to Variables to be mappable**:
- `#f9f9f9` — input background (should become `Surface/Input`)
- `#cacaca` — input border (should become `Border/Input`)
- `#605f64` — currency switcher muted text (near-duplicate of `textLightGray`)
- `rgba(0,112,201,0.15)` — AI input focus shadow (should become `Feedback/Focus`)

**Typography collection** (two scale groups, mobile + desktop):
```
Mobile: mxLarge=22px, mLarge=20px, mMedium=14px, mSmall=12px
Desktop: dxLarge=58px, dLarge=40px, dMedium=18px, dSmall=16px, nano=8px
Font-weight map: bold=800, semiBold=700, regular=500, light=400
Font family: Open Sans (Google Fonts)
```

---

## Gaps Before Code Connect Is Useful

### Gap 1 — No Figma File Exists

There is no Figma design file for this project. Code Connect links a Figma component node ID to a React component. Without a Figma file, there is nothing to link.

**Action required**: Create a Figma file and build components that match the React component inventory above.

### Gap 2 — No Storybook (Component Isolation)

Code Connect benefits from Storybook because it can generate stories from connected components. None exists. Without Storybook, there is no way to see isolated component states without running the full Next.js app.

**Action required**: Add Storybook and write stories for at minimum `Button`, `Input`, `Select`, `ProductCard`, `ProductPrice`, `CartDropdown`.

### Gap 3 — Button Is a Styled-Component, Not a Function Component

`Button` is defined as `const Button = styled.button<...>`. Code Connect works best with function components that have explicit prop interfaces. The `$type` prop variant logic is embedded in the template literal, not in a clearly typed props interface with JSDoc.

**Action required**: Either wrap Button in a function component that exposes `type` as a prop, or ensure the Code Connect config explicitly enumerates the variant values.

### Gap 4 — Input Conflates Two Controls

`Input` renders either an `<input>` or a `<select>` based on `type='select'`. This means one React component maps to two conceptually different Figma components (Text Field and Dropdown). Code Connect only supports one-to-one mappings.

**Action required**: Split `Input` into `TextInput` and `SelectInput`, or create two separate Code Connect configurations pointing to the same file with different property maps.

### Gap 5 — Hardcoded Colors Not in Theme

Seven color values are hardcoded in styled-component files rather than using theme tokens (listed in `detail.md`). These cannot be mapped to Figma Variables because they are not tokens.

**Action required**: Migrate hardcoded values to `Theme.ts` before creating Figma Variable mappings.

### Gap 6 — No Semantic Token Layer

Theme tokens use implementation-level names (`otelBlue`, `mLarge`) rather than semantic names (`color.primary.action`, `typography.heading.lg`). Figma Variables work best with semantic naming because the same visual value can have different semantic roles.

**Action required** (optional but recommended): Add a semantic alias layer in `Theme.ts` on top of the existing primitive values before syncing to Figma.

### Gap 7 — ProductCard Image Is Not a Composable Slot

The product image in `ProductCard` is a CSS `background-image` on a `<div>`, not a `<img>` or Next.js `<Image>`. Figma would represent this as an image layer. Code Connect cannot map a Figma image layer to a CSS background property in a useful way.

**Action required**: Replace the CSS background-image approach with `<img>` or `<Image>` to unlock proper slot mapping and fix the missing `alt` accessibility issue simultaneously.

### Gap 8 — No Code Connect Config File

No `.figma/` directory or `figma.config.json` file exists.

**Action required**: After addressing the above gaps, add a Code Connect configuration and link each component to its Figma node ID.

---

## Recommended Sequencing

1. Fix `Input` label association (accessibility + cleaner component split)
2. Replace `ProductCard` background-image with `<img>`
3. Migrate hardcoded colors to `Theme.ts`
4. Add Storybook with stories for the six primitive/atom components
5. Create Figma file with component library matching the inventory
6. Create Figma Variables collection mirroring `Theme.ts`
7. Initialize Code Connect config and link components one by one, starting with `Button`

