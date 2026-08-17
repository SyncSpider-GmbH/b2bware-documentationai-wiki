---
title: Styling
description: Tailwind-first styling and the fixed head cascade.
---

<Info>
This page also ships inside the default theme download under `docs/11-styling.md`, so offline and AI-assisted authors have the same contract locally. This online version is always the latest.
</Info>

## 10. Styling — Tailwind first

**Strongly prefer Tailwind utility classes over custom CSS.** Every layout already links the platform's prebuilt `base.css` (Tailwind v4, compiled once at deploy time), which ships a large set of utilities and the full design-token system. Using Tailwind keeps theme zips tiny and pages light — no extra CSS is shipped per theme unless you actually write some.

### 10.1 Order of preference

1. **Tailwind utility classes** — first choice for everything (layout, spacing, color, typography, responsive, dark mode, hover/focus states).
2. **CSS variable overrides** in `assets/css/storefront.css` — re-skin the theme by redeclaring `--brand-*` tokens. No new selectors needed. Decide per token whether the theme owns it or Appearance may override it (§11.8.1).
3. **Custom CSS classes** in `assets/css/storefront.css` — only when a utility composition is genuinely impossible or would bloat markup beyond readability.
4. **Inline `style="..."`** — last resort, only for truly one-off values (e.g. a computed `background-image: url(...)`).

Avoid:
- Re-implementing utilities Tailwind already provides
- Writing `<style>` blocks inside blade files (allowed, but discouraged — moves CSS out of the cacheable file)
- Hardcoding hex colors, px values, or font names — always reach for a token

### 10.1.1 The head cascade (do not reorder)

The stylesheet order in `layouts/shop.blade.php` is a **contract**, because later layers intentionally win over earlier ones. The default layout emits, in this exact order:

1. **`@storefrontColorScheme`** — sets `light`/`dark` on `<html>` *before* any stylesheet, so scheme-scoped variables resolve on first paint (no flash). See §11.10.
2. **Platform `base.css`** (`@storefrontAsset('base.css')`) — Tailwind build + the full token system + `.storefront-richtext` defaults.
3. **Tenant brand + fonts** — `{!! $tenantBrandCss !!}` and `{!! $tenantFontsHtml !!}` from the b2bware Appearance settings (the tenant's `--brand-*` overrides and `@font-face`/`<link>` font declarations).
4. **Theme CSS** — `@themeAsset('css/storefront.css')` if your theme ships one. This is where a theme redeclares `--brand-*` tokens or adds custom classes.
5. **Per-customer branding** — `{!! $brandingCss !!}` (category colour ramp etc.), last so it can win where the platform intends.

Keep this order. Moving theme CSS above the tenant brand block, or omitting `@storefrontColorScheme`, breaks tenant Appearance overrides and causes a light/dark flash. A theme decides **per token** whether it owns the value (declare it in theme CSS, step 4) or lets Appearance win (leave it to step 3) — see §11.8.1.

### 10.2 Token system at a glance

The platform exposes every design decision through two layers:

- **`--brand-*`** — author-facing override layer. Theme CSS sets these in `assets/css/storefront.css`. The full enumerated list lives in **§11 — Design tokens reference** below.
- **`--color-*`, `--text-*`, `--radius`, `--container-*`, `--font-*`** — Tailwind-internal layer, consumed by utility classes. Do **not** redeclare these in a theme; override the matching `--brand-*` variable instead.

**Color families** (every family ships shades `50 100 200 300 400 500 600 700 800`):

```
primary  secondary  success  warning  error  info  neutral  surface
```

The plain (unshaded) name maps to the `500` shade by default (e.g. `bg-primary` == `bg-primary-500`).

**Neutral extras**: `text-neutral-white`, `text-neutral-black`, `bg-neutral-white`, `bg-neutral-black`.

**Semantic singletons** (not part of a numeric scale):

```
backdrop  tooltip  headings  body  placeholder
```

**Surface tokens** (page chrome, cards, inputs, status banners):

| Utility                                        | Purpose                                |
| ---------------------------------------------- | -------------------------------------- |
| `bg-surface-page`                              | Page background                        |
| `bg-surface-card`                              | Card / panel background                |
| `bg-surface-input`                             | Form input background                  |
| `bg-surface-disabled`                          | Disabled element background            |
| `bg-surface-{success,warning,info,error}-subtle`        | Tinted status banners         |
| `text-surface-{success,warning,info,error,disabled}-subtle-content` | Status text on subtle bg |
| `border-surface-input-stroke`                  | Input border                           |
| `border-surface-{success,warning,info,error,disabled}-subtle-stroke` | Status border       |

**Typography**:

```
font-primary   font-secondary
text-xs text-sm text-base text-lg text-xl text-2xl ... text-9xl
font-thin font-extralight font-light font-normal font-medium font-semibold font-bold font-extrabold font-black
leading-tight leading-snug leading-normal leading-relaxed leading-loose
tracking-tight tracking-normal tracking-wide tracking-wider tracking-widest
```

**Radius**: `rounded`, `rounded-sm`, `rounded-md`, `rounded-lg`, `rounded-xl`, `rounded-2xl`, `rounded-3xl`, `rounded-full`, `rounded-none` — plus `rounded-{t,r,b,l}-*` for sides and `rounded-{tl,tr,br,bl}-*` for corners.

**Breakpoints** (responsive prefixes, baked in at build time — cannot be overridden at runtime):

```
sm:        (640px)
md:        (768px — same as `tablet:`)
lg:        (1024px)
xl:        (1280px — same as `desktop:`)
tablet:    (768px)
desktop:   (1280px)
```

Plus numeric breakpoints: `320:` `360:` `420:` `480:` `640:` `800:` `1024:` `1280:` `1360:` `1366:` `1440:` `1536:` `1600:` `1920:` `2048:` `2560:` `3440:` `3840:` — match the same numeric `--container-*` widths.

**Container widths**: `max-w-{320,360,420,480,640,tablet,800,1024,1280,desktop,1360,1366,1440,1536,1600,1920,2048,2560,3440,3840}`.

**Dark mode**: driven by a `.dark` class on the document root (`<html>`), set before first paint by `@storefrontColorScheme`. The whole palette re-skins through the design tokens, so you rarely write dark-specific CSS — and you must **not** add new `dark:` utility classes (only a small precompiled set exists in `base.css`; new ones silently no-op). Build a toggle, swap light/dark logos, and tune `:root.dark` tokens as described in §11.10.


### 10.3 Tailwind cheatsheet for theme blades

```blade
{{-- Layout / spacing --}}
<div class="flex items-center justify-between gap-4 p-4 md:p-6">

{{-- Cards & surfaces --}}
<article class="bg-surface-card rounded-lg shadow-sm p-6 border border-surface-input-stroke">

{{-- Typography --}}
<h1 class="font-primary text-3xl font-semibold text-primary-700 dark:text-primary-200">

{{-- Buttons (use semantic color families, not raw hex) --}}
<button class="bg-primary text-primary-content hover:bg-primary-600 rounded px-4 py-2 transition-colors">

{{-- Subtle status banner --}}
<div class="bg-surface-warning-subtle text-surface-warning-subtle-content rounded p-3">

{{-- Responsive grid --}}
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

{{-- Container width --}}
<main class="mx-auto max-w-desktop px-4">
```

> **Responsive table → cards (worked example).** The product page's "Choose variants" bulk table reflows into one card per variant below `md` using `max-md:` overrides on the table elements plus `md:hidden` label spans (see *Configurable products (variants)*) — **no custom CSS**. Caveat: `max-*` (max-width) variants are **not** in the precompiled set — exactly like new `dark:` classes (§10.2), they silently no-op unless added to the `@source inline("…")` allowlist in `resources/css/storefront.css` and `base.css` is rebuilt (`npm run build:assets`, with the **same pinned Tailwind version** so the rebuild stays additive).

### 10.4 When custom CSS is OK

Add a rule to `assets/css/storefront.css` only when one of these is true:

- The selector targets a deeply nested third-party widget you don't control
- It implements a complex animation/keyframe sequence
- It applies a pseudo-element (`::before`, `::after`) effect that would be noisier as a wrapper element
- It re-asserts a native control reset that the platform Preflight clears — e.g. `dialog { margin: auto }` to re-center `<dialog>` modals (required for any theme using modals; see §9 "Modals")
- It overrides a `--brand-*` token (the primary intended use of that file)

Example — pure variable overrides, zero new selectors:

```css
:root {
    --font-primary: "Inter", sans-serif;
    --brand-color-primary-500: #ff6a00;
    --brand-color-primary-600: #cc5500;
    --brand-radius: 0.75rem;
}

:root.dark {
    --brand-color-surface-page: #14131a;
}
```

### 10.5 Forbidden styling patterns

- Loading Tailwind from a CDN inside a layout — the platform already ships it
- Adding a `@tailwind` / `@import "tailwindcss"` directive in theme CSS — there is no build step at upload
- Hardcoded hex/rgb colors in markup (`style="color: #2563eb"`) when a token exists (`text-primary-500`)
- Arbitrary value utilities for tokens that exist (`text-[#2563eb]` → use `text-primary-500`)
- Hardcoding `font-family` on individual selectors — load the font once (Google Fonts or self-hosted, see §11.1) then point `--font-primary` (headings) / `--font-secondary` (body copy) at it so the base `h1`–`h6` / `body` styles and every `font-primary` / `font-secondary` utility follow automatically
- Inline `<style>` blocks that re-implement utility behavior already in `base.css`

### 10.6 Action icons & tap targets

Every interactive icon control — an icon-only button or link such as a favorite, remove, edit, close (`×`), view-toggle or social link — **must present a tap target of at least 24×24px**. Mobile visitors struggle to activate anything smaller (this is also the WCAG 2.5.8 minimum target size).

- Size the **control**, not just the glyph. A small SVG or text glyph inside an unsized button is only as tappable as the glyph. Give the button/link a fixed box, e.g. `inline-flex h-8 w-8 items-center justify-center` (32px, comfortable) or at minimum `h-6 w-6` (24px) — never leave an icon control at `p-0` with a 16px icon.
- Icons themselves should read at ~24px (`h-6 w-6`) for primary actions; a 20px icon is acceptable only inside a ≥24px tap box.
- Native form controls follow the same floor: checkboxes and radios are re-skinned to 24px in `assets/css/storefront.css` (§10.4). Don't ship smaller ones.
- This applies to duplicated inline markup too. Each `<dialog>` in the default theme carries its own close button rather than sharing one, so the 24px floor has to be repeated in every copy.

---
