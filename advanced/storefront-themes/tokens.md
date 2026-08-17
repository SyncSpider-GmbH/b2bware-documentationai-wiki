---
title: Design tokens
description: The complete design-token variable reference and dark mode.
---

<Info>
This page also ships inside the default theme download under `docs/12-tokens.md`, so offline and AI-assisted authors have the same contract locally. This online version is always the latest.
</Info>

## 11. Design tokens — complete variable reference

Every `--brand-*` variable listed below is overridable from `assets/css/storefront.css`. Each variable lists its **default value** and the **Tailwind utility(ies)** it powers, so you know exactly which classes change when you redeclare it.

> **Before you redeclare anything, read §11.8.1.** Your stylesheet loads *after* the store owner's Appearance settings, so a plain `:root` declaration means "this theme owns this token" and the owner can no longer change it from the admin. Wrap it in `@layer theme-defaults` instead when you want it to be a default Appearance can still override. This applies to the fonts below just as much as to the colours.

### 11.1 Fonts

| Variable           | Default                | Powers                                                  |
| ------------------ | ---------------------- | ------------------------------------------------------- |
| `--font-primary`   | `"Roboto", sans-serif` | `font-primary` utility **and** the base `h1`–`h6` font  |
| `--font-secondary` | `"Roboto", sans-serif` | `font-secondary` utility **and** the base `body` font    |

> Fonts are the **only** family without the `--brand-*` prefix. Override `--font-primary` / `--font-secondary` directly.

Redeclaring a variable in your theme's `assets/css/storefront.css` `:root` is enough to re-skin **every** element that uses it — all headings and the `font-primary` utility follow `--font-primary`; `body` copy and the `font-secondary` utility follow `--font-secondary`. You never touch `font-family` on individual selectors.

But a variable only names a typeface — the browser still has to **load** it. Integrating a custom font is always two steps:

1. **Load the font** — make the `@font-face` rules available (hosted by Google, or self-hosted from `assets/fonts/`).
2. **Point the variable at it** — set `--font-primary` / `--font-secondary` in `:root`, always ending the stack with a system fallback (`sans-serif`, `serif`, …) so text renders before the font arrives and if the request fails.

Pick one of the three approaches below.

#### Approach A — Google Fonts via `<link>` (fastest hosted option)

Add the Google Fonts `<link>` tags to the document `<head>` with `@push('head')` (the canonical layouts all expose a `@stack('head')` slot), then set the variable in `assets/css/storefront.css`. The two `preconnect` hints let the browser open the connection to Google's font CDN early, so this loads faster than `@import`.

```blade
{{-- In a layout or page: opens the font CDN connection early, then loads the face --}}
@push('head')
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap">
@endpush
```

```css
/* assets/css/storefront.css — wire the loaded family to the token */
:root {
    --font-primary: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
}
```

> Always request `&display=swap` so text is visible in the fallback font while the web font downloads (no invisible-text flash).

#### Approach B — Google Fonts via CSS `@import` (single file, simplest)

Put a CSS `@import` at the **very top** of `assets/css/storefront.css` (before any rule — that's a CSS requirement), then set the variable below it. Everything lives in one file, but the font CSS is fetched only after `storefront.css` itself downloads (one extra round-trip), so Approach A is faster for above-the-fold text.

```css
/* assets/css/storefront.css */
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap");

:root {
    --font-primary: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
}
```

> `@import` here loads a **font stylesheet** — this is fine and fully supported. It is **not** the forbidden `@import "tailwindcss"` from §10.5 (that one needs a build step the platform doesn't run on upload).

#### Approach C — Self-hosted (recommended; GDPR-safe, fastest, offline-proof)

Download the font's `.woff2` files (e.g. from [google-webfonts-helper](https://gwfh.mranftl.com/fonts) for Google fonts), drop them in `assets/fonts/` (see the §3 whitelist — `.woff .woff2 .ttf .otf`), declare `@font-face` in `assets/css/storefront.css` pointing at them with a **relative** path, then set the variable. No third-party request at runtime: the visitor's IP is never sent to Google (the practice a German court ruled a GDPR violation in 2022), so this is the right default for EU storefronts.

```css
/* assets/css/storefront.css */
@font-face {
    font-family: "Inter";
    font-style: normal;
    font-weight: 400;
    font-display: swap;                 /* show fallback text immediately */
    src: url("../fonts/inter-400.woff2") format("woff2");
}
@font-face {
    font-family: "Inter";
    font-style: normal;
    font-weight: 700;
    font-display: swap;
    src: url("../fonts/inter-700.woff2") format("woff2");
}

:root {
    --font-primary: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
}
```

> Paths in theme CSS are relative to `assets/css/`, so `../fonts/<file>.woff2` resolves to `assets/fonts/`. Ship only the weights you use — each extra weight is a separate download.

#### Pairing two fonts

Set both variables when the design uses a display face for headings and a text face for body copy — `--font-primary` drives every `h1`–`h6` automatically:

```css
:root {
    --font-primary:   "Playfair Display", Georgia, serif;                     /* headings */
    --font-secondary: "Inter", -apple-system, BlinkMacSystemFont, sans-serif; /* body */
}
```

| Need                                                  | Use                          |
| ----------------------------------------------------- | ---------------------------- |
| Quick prototype, non-EU traffic, fewest files         | Approach A (`<link>`)        |
| Everything in one CSS file, simplicity over speed     | Approach B (`@import`)       |
| Production / EU storefront / privacy / best performance | **Approach C (self-hosted)** |

### 11.2 Radius

| Variable         | Default     | Powers utilities                |
| ---------------- | ----------- | ------------------------------- |
| `--brand-radius` | `0.25rem`   | `rounded` and every `rounded-*` |

### 11.3 Typography scale

| Variable                              | Default     | Powers utility |
| ------------------------------------- | ----------- | -------------- |
| `--brand-text-xs`                     | `0.875rem`  | `text-xs`      |
| `--brand-text-xs-line-height`         | `1.25rem`   | `text-xs` LH   |
| `--brand-text-sm`                     | `1rem`      | `text-sm`      |
| `--brand-text-sm-line-height`         | `1.5rem`    | `text-sm` LH   |
| `--brand-text-base`                   | `1.125rem`  | `text-base`    |
| `--brand-text-base-line-height`       | `1.625rem`  | `text-base` LH |
| `--brand-text-lg`                     | `1.25rem`   | `text-lg`      |
| `--brand-text-lg-line-height`         | `1.75rem`   | `text-lg` LH   |

> `text-xl` and above use Tailwind's built-in scale and are not currently exposed as `--brand-*`.

### 11.4 Containers (max-widths)

Each variable maps to one `max-w-*` utility. Defaults are in px and match the variable suffix.

```
--brand-container-320      →  max-w-320      (default 320px)
--brand-container-360      →  max-w-360
--brand-container-420      →  max-w-420
--brand-container-480      →  max-w-480
--brand-container-640      →  max-w-640
--brand-container-tablet   →  max-w-tablet   (default 768px)
--brand-container-800      →  max-w-800
--brand-container-1024     →  max-w-1024
--brand-container-1280     →  max-w-1280
--brand-container-desktop  →  max-w-desktop  (default 1280px)
--brand-container-1360     →  max-w-1360
--brand-container-1366     →  max-w-1366
--brand-container-1440     →  max-w-1440
--brand-container-1536     →  max-w-1536
--brand-container-1600     →  max-w-1600
--brand-container-1920     →  max-w-1920
--brand-container-2048     →  max-w-2048
--brand-container-2560     →  max-w-2560
--brand-container-3440     →  max-w-3440
--brand-container-3840     →  max-w-3840
```

### 11.5 Brand color scales

Each color family has 9 shades plus an alias. All overrides follow the pattern `--brand-color-{family}-{shade}`.

#### Primary

| Variable                       | Default   | Powers utilities                              |
| ------------------------------ | --------- | --------------------------------------------- |
| `--brand-color-primary-50`     | `#eef4fe` | `bg-primary-50`, `text-primary-50`, `border-primary-50` |
| `--brand-color-primary-100`    | `#d9e6fc` | `*-primary-100`                               |
| `--brand-color-primary-200`    | `#b3cdf9` | `*-primary-200`                               |
| `--brand-color-primary-300`    | `#7ca8f4` | `*-primary-300`                               |
| `--brand-color-primary-400`    | `#4d82f1` | `*-primary-400`                               |
| `--brand-color-primary-500`    | `#2b62f0` | `*-primary-500`                               |
| `--brand-color-primary`        | inherits `500` | `bg-primary`, `text-primary`, `border-primary` |
| `--brand-color-primary-600`    | `#234fc2` | `*-primary-600`                               |
| `--brand-color-primary-700`    | `#1b3c94` | `*-primary-700`                               |
| `--brand-color-primary-800`    | `#132866` | `*-primary-800`                               |
| `--brand-color-primary-content` | auto-derived | `text-primary-content`, `bg-primary-content` |
| `--brand-color-primary-subtle` | 14% of `--color-primary` | `bg-primary-subtle`     |
| `--brand-color-primary-subtle-stroke` | 34% of `--color-primary` | `border-primary-subtle-stroke` |

> **Use `bg-primary-subtle` for "marked with the brand colour" states** — the
> selected category, the chosen address, a step badge — not `bg-primary-50`.
> Like `bg-surface-hover` (§11.7) it is a translucent wash rather than an opaque
> tint, because these fills land on the page *and* on cards, and a light tint
> picked to read on white is a near-white block over a dark storefront.

> **Always pair `bg-primary` with `text-primary-content`, never `text-neutral-white`.**
> White is only legible on a *dark* brand colour. On a light one — a gold, a
> lime, a pastel — white text scores around 1.6:1, far below the 4.5:1 WCAG AA
> floor, and the label becomes unreadable. `--brand-color-primary-content` is
> derived from the configured ramp: the platform picks the stop from the
> family's **own** shades that clears AAA (7:1) against the base, so the label
> stays on-brand rather than flat black, and deepens the hue further only when
> no stop is contrasty enough. The store owner can override it from
> **Appearance → Text on brand colours**.
>
> **A theme that owns its primary must own the foreground too.** If you declare
> `--brand-color-primary-*` unlayered (§11.8.1), the auto-derived value is
> computed from the *Appearance* colour, not yours — so declare
> `--brand-color-primary-content` alongside your ramp. The same applies to
> `--brand-color-secondary-content`.

#### Secondary

| Variable                          | Default   |
| --------------------------------- | --------- |
| `--brand-color-secondary-50`      | `#e8e8ed` |
| `--brand-color-secondary-100`     | `#d0d1da` |
| `--brand-color-secondary-200`     | `#a2a4b6` |
| `--brand-color-secondary-300`     | `#737691` |
| `--brand-color-secondary-400`     | `#45496d` |
| `--brand-color-secondary-500`     | `#161b48` |
| `--brand-color-secondary`         | inherits `500` |
| `--brand-color-secondary-600`     | `#12163a` |
| `--brand-color-secondary-700`     | `#12163a` |
| `--brand-color-secondary-800`     | `#0d102b` |
| `--brand-color-secondary-content` | auto-derived |

#### Success

| Variable                         | Default   |
| -------------------------------- | --------- |
| `--brand-color-success-50`       | `#e6f7ef` |
| `--brand-color-success-100`      | `#cdefdf` |
| `--brand-color-success-200`      | `#9adfc0` |
| `--brand-color-success-300`      | `#68d0a0` |
| `--brand-color-success-400`      | `#35c081` |
| `--brand-color-success-500`      | `#03b061` |
| `--brand-color-success`          | inherits `500` |
| `--brand-color-success-600`      | `#028d4e` |
| `--brand-color-success-700`      | `#026a3a` |
| `--brand-color-success-800`      | `#014627` |

#### Warning

| Variable                         | Default   |
| -------------------------------- | --------- |
| `--brand-color-warning-50`       | `#fef6e9` |
| `--brand-color-warning-100`      | `#fdedd3` |
| `--brand-color-warning-200`      | `#fbdba7` |
| `--brand-color-warning-300`      | `#f9ca7b` |
| `--brand-color-warning-400`      | `#f7b84f` |
| `--brand-color-warning-500`      | `#f5a623` |
| `--brand-color-warning`          | inherits `500` |
| `--brand-color-warning-600`      | `#c4851c` |
| `--brand-color-warning-700`      | `#936415` |
| `--brand-color-warning-800`      | `#62420e` |

#### Error

| Variable                       | Default   |
| ------------------------------ | --------- |
| `--brand-color-error-50`       | `#ffece9` |
| `--brand-color-error-100`      | `#ffdad3` |
| `--brand-color-error-200`      | `#ffb5a8` |
| `--brand-color-error-300`      | `#ff8f7c` |
| `--brand-color-error-400`      | `#ff6a51` |
| `--brand-color-error-500`      | `#ff4525` |
| `--brand-color-error`          | inherits `500` |
| `--brand-color-error-600`      | `#cc371e` |
| `--brand-color-error-700`      | `#992916` |
| `--brand-color-error-800`      | `#661c0f` |

#### Info

| Variable                      | Default   |
| ----------------------------- | --------- |
| `--brand-color-info-50`       | `#f2eef9` |
| `--brand-color-info-100`      | `#e5ddf3` |
| `--brand-color-info-200`      | `#cbbce7` |
| `--brand-color-info-300`      | `#b29ada` |
| `--brand-color-info-400`      | `#9879ce` |
| `--brand-color-info-500`      | `#7e57c2` |
| `--brand-color-info`          | inherits `500` |
| `--brand-color-info-600`      | `#65469b` |
| `--brand-color-info-700`      | `#4c3474` |
| `--brand-color-info-800`      | `#32234e` |

#### Neutral

| Variable                          | Default   |
| --------------------------------- | --------- |
| `--brand-color-neutral-50`        | `#ecedee` |
| `--brand-color-neutral-100`       | `#dadbdd` |
| `--brand-color-neutral-200`       | `#b4b6bb` |
| `--brand-color-neutral-300`       | `#8f9299` |
| `--brand-color-neutral-400`       | `#696d77` |
| `--brand-color-neutral-500`       | `#444955` |
| `--brand-color-neutral`           | inherits `500` |
| `--brand-color-neutral-600`       | `#363a44` |
| `--brand-color-neutral-700`       | `#292c33` |
| `--brand-color-neutral-800`       | `#1b1d22` |
| `--brand-color-neutral-white`     | `#ffffff` |
| `--brand-color-neutral-black`     | `#000000` |

#### Surface (warm beige scale, for paper-like UI)

| Variable                          | Default   |
| --------------------------------- | --------- |
| `--brand-color-surface-50`        | `#fefefd` |
| `--brand-color-surface-100`       | `#fefdfb` |
| `--brand-color-surface-200`       | `#fcfaf7` |
| `--brand-color-surface-300`       | `#fbf8f4` |
| `--brand-color-surface-400`       | `#f9f5f0` |
| `--brand-color-surface-500`       | `#f8f3ec` |
| `--brand-color-surface`           | inherits `500` |
| `--brand-color-surface-600`       | `#dfdbd4` |
| `--brand-color-surface-700`       | `#c6c2bd` |
| `--brand-color-surface-800`       | `#aeaaa5` |

### 11.6 Semantic text tokens

| Variable                       | Default                  | Powers utilities                     |
| ------------------------------ | ------------------------ | ------------------------------------ |
| `--brand-color-headings`       | `--color-neutral-800`    | `text-headings`, base `h1`–`h6` color |
| `--brand-color-body`           | `--color-neutral-700`    | `text-body`, base `<body>` color      |
| `--brand-color-placeholder`    | `--color-neutral-400`    | `text-placeholder`, `::placeholder`   |

### 11.7 Semantic surface tokens

#### Page chrome

| Variable                       | Default                  | Powers utility       |
| ------------------------------ | ------------------------ | -------------------- |
| `--brand-color-surface-page`   | `#f4f5f7`                | `bg-surface-page`    |
| `--brand-color-surface-card`   | `--color-neutral-white`  | `bg-surface-card`    |
| `--brand-color-surface-hover`  | 8% of `--color-body`     | `bg-surface-hover`   |
| `--brand-color-surface-active` | 14% of `--color-body`    | `bg-surface-active`  |

**Use `hover:bg-surface-hover` for hover states — not a numbered `bg-surface-*`.**
Hover targets live in three different places: on the page, on a card, and
inside the header, each a different colour. No opaque value can look right on
all three — a fill picked to read well on a white card flashes near-white over
a dark page, and one picked for a dark page disappears on a card. The hover
token is instead a **translucent wash of the body text colour**, so it darkens
a light surface, lightens a dark one, and composites correctly over whatever it
happens to sit on. Use `bg-surface-active` for the pressed / selected step.

The numbered `bg-surface-50…800` scale stays what it always was: an opaque
decorative tint. Reach for it for static fills, not interaction states.

#### Borders

| Variable                          | Default      | Powers utility           |
| --------------------------------- | ------------ | ------------------------ |
| `--brand-color-border-subtle`     | `#eceef2`    | `border-border-subtle`   |
| `--brand-color-border`            | inherits subtle | `border-border`       |

#### Status surfaces (subtle tinted banners — triple set per status)

For each of **success / warning / info / error**:

| Variable                                           | Default ref                  | Powers utility                                            |
| -------------------------------------------------- | ---------------------------- | --------------------------------------------------------- |
| `--brand-color-surface-{status}-subtle`            | `--color-{status}-50`        | `bg-surface-{status}-subtle`                              |
| `--brand-color-surface-{status}-subtle-content`    | `--color-{status}-500`       | `text-surface-{status}-subtle-content`                    |
| `--brand-color-surface-{status}-subtle-stroke`     | `--color-{status}-200`       | `border-surface-{status}-subtle-stroke`                   |

#### Disabled

| Variable                                           | Default                  | Powers utility                          |
| -------------------------------------------------- | ------------------------ | --------------------------------------- |
| `--brand-color-surface-disabled`                   | `--color-neutral-50`     | `bg-surface-disabled`                   |
| `--brand-color-surface-disabled-content`           | `--color-neutral-300`    | `text-surface-disabled-subtle-content`  |
| `--brand-color-surface-disabled-stroke`            | `--color-neutral-100`    | `border-surface-disabled-subtle-stroke` |

#### Form inputs

| Variable                                           | Default                  | Powers utility                          |
| -------------------------------------------------- | ------------------------ | --------------------------------------- |
| `--brand-color-surface-input`                      | `--color-neutral-white`  | `bg-surface-input`                      |
| `--brand-color-surface-input-content`              | `--color-neutral-800`    | (text color of input contents)          |
| `--brand-color-surface-input-placeholder`          | `--color-neutral-400`    | (placeholder text in inputs)            |
| `--brand-color-surface-input-stroke`               | `--color-neutral-200`    | `border-surface-input-stroke`           |

### 11.8 Tooltip & backdrop

| Variable                          | Default                  | Powers utility            |
| --------------------------------- | ------------------------ | ------------------------- |
| `--brand-color-tooltip`           | `--color-neutral-800`    | `bg-tooltip`              |
| `--brand-color-tooltip-content`   | `--color-neutral-white`  | (tooltip text color)      |
| `--brand-color-backdrop`          | `--color-neutral-black`  | `bg-backdrop`             |

### 11.8.1 Appearance settings and the CSS cascade

Store owners configure the Storefront palette, semantic colours, and fonts in
**B2BWare admin → Store setup → Appearance**. Those settings apply to every
theme, including uploaded custom themes.

The platform owns this load order:

1. `base.css` — the compiled utility and default-token layer.
2. The tenant Appearance block (`:root` and `:root.dark`) — palette, semantic
   tokens, and fonts selected by the store owner.
3. The active theme's `assets/css/storefront.css` — theme tokens and
   structural styles.
4. The per-customer branding block — customer-category primary/secondary ramps.

**The theme stylesheet loads after Appearance, so a theme decides whether it
owns a token or defers to the store owner.** You choose per declaration:

| You want | Declare it | Result |
| --- | --- | --- |
| The theme **owns** this colour | plain `:root` / `:root.dark` | Beats Appearance — the store owner cannot change it |
| Appearance stays **in control** | inside `@layer theme-defaults` | Your value applies until the owner configures Appearance, then Appearance wins |

A layered declaration always loses to an unlayered one *regardless of document
order*, which is what makes the second row work even though your stylesheet
loads last.

Two things soften this in practice. Appearance only emits the families and
tokens the owner has **actually configured**, so an unconfigured Appearance page
never touches your theme either way. And the per-customer branding block is
always last, so customer-category ramps still override both.

The bundled default theme takes the deferring option, because a tenant on the
default theme should be able to re-skin the whole storefront from Appearance:

```css
/* Defaults — Appearance overrides these when the owner configures it. */
@layer theme-defaults {
    :root {
        --font-primary: "Outfit", sans-serif;
        --brand-color-primary-500: #3260e7;
    }

    :root.dark {
        --brand-color-surface-page: #111318;
    }
}
```

A theme shipped for one brand normally wants the opposite — its palette is part
of the design, not a suggestion:

```css
/* Owned — this theme is always gold, whatever Appearance says. */
:root {
    --brand-radius: 0.5rem;
    --brand-color-primary-500: #c8a24a;
}
```

**Never use `!important` to force a tenant-facing token,** and do not reach for
selectors such as `html:root`, `html.dark:root`, or
`html.dark body { --brand-* }`. If you want the token, declare it unlayered; if
you don't, layer it. Raising specificity only breaks the store owner's controls
in ways neither option does. Equally, do not hardcode brand colours on element
selectors when a token utility exists.

Use token-backed utilities in markup:

```blade
<header class="bg-secondary-800 text-neutral-white">
    <a class="text-primary" href="@routeUrl('store.home')">@t('Home')</a>
</header>
```

For element-specific layout or interaction styles that have no Appearance token,
ordinary theme selectors remain appropriate.

### 11.9 What you **cannot** override

These are baked at build time (CSS spec disallows `var()` inside `@media`):

- `--breakpoint-*` — the responsive cutoffs (`sm:`, `md:`, `tablet:`, `desktop:`, etc.). Change them only by rebuilding the platform.

These are intentionally Tailwind-internal — overriding them in a theme is unsupported:

- All `--color-*`, `--text-*`, `--container-*`, `--radius` tokens — override the matching `--brand-*` instead.

### 11.10 Dark mode

The storefront has first-class light/dark mode. It is driven by a single `.dark` class on the document root (`<html>`), and it re-skins almost entirely through the design tokens — so in most themes you write **no** dark-specific CSS at all.

#### How it's wired (platform-owned)

- **Root class.** When a dark preference is active, the layout renders `<html class="dark">`. The platform `base.css` redeclares the full `--brand-*` surface / text / border / input palette under `.dark`, and CSS custom properties inherit — so every `bg-surface-page`, `text-body`, `bg-surface-card`, `border-border-subtle`, input and status-subtle token flips automatically on `<body>` and all descendants.
- **No flash (`@storefrontColorScheme`).** Place this directive once in `<head>`, before your stylesheets (the canonical layouts already do). It emits `<meta name="color-scheme">` and a tiny **synchronous** script that sets the `.dark` class *before first paint*, from the saved cookie or — when there is no cookie — the visitor's OS `prefers-color-scheme`. This is the one sanctioned non-module inline script; never replicate it as a deferred module (it would paint the wrong scheme first).
- **Preference + persistence.** The active scheme is resolved server-side from the `storefront_color_scheme` cookie and exposed to every blade as `$colorScheme` (`'light'`, `'dark'`, or `null` when unset). The toggle persists the choice via `POST` to `store.color-scheme.set` (the `color-scheme` form type, §9.5), so the next navigation already renders the right scheme server-side.
- **Both schemes are emitted upfront — switching is purely client-side.** The platform injects *both* the light and the dark configuration into every page, so toggling `.dark` recolours and re-images everything instantly without a server round-trip:
  - **Palette, semantic colours, and fonts.** The store owner's Storefront palette and semantic settings (B2BWare admin → Store setup → Appearance) are emitted as `--brand-color-*` declarations under `:root { … }` (light) and `:root.dark { … }` (dark). They load **before** the theme stylesheet, so they override the platform defaults but yield to any token the theme declares unlayered; see §11.8.1. Per-customer category branding is emitted last and layers on top of the primary/secondary ramps.
  - **Logos & login background** ship a light and a dark variant in the markup, revealed by CSS keyed on `.dark` (below). No `dark:` utilities, no reload.

#### Building a light/dark toggle

Render it as a no-JS form with **two** submit buttons (one per scheme) and let CSS reveal the one matching the active root class. This stays correct even with JS off and an OS-driven scheme. Progressive enhancement flips it live without a reload:

```blade
@storefrontForm('color-scheme', ['data-theme-toggle' => true])
    <input type="hidden" name="redirect" value="{{ $currentPath ?? '/' }}">
    <button type="submit" name="scheme" value="dark"  class="to-dark"  aria-label="@t('Switch to dark mode')">🌙</button>
    <button type="submit" name="scheme" value="light" class="to-light" aria-label="@t('Switch to light mode')">☀️</button>
@endstorefrontForm
```

```css
/* show only the button for the *other* scheme */
.to-light { display: none; }
:root.dark .to-dark  { display: none; }
:root.dark .to-light { display: inline-flex; }
```

```blade
{{-- live toggle (no reload) when the runtime is present; plain POST otherwise --}}
<script type="module">
    for (const form of document.querySelectorAll('[data-theme-toggle]')) {
        form.addEventListener('submit', (event) => {
            const api = window.Storefront;
            if (api && typeof api.toggleColorScheme === 'function') {
                event.preventDefault();
                api.toggleColorScheme();
            }
        });
    }
</script>
```

> The hidden `redirect` field must be a **relative** path (`$currentPath` is the current request URI); `SafeRedirect` rejects absolute URLs, so `@routeUrl` will not work here. `Storefront.toggleColorScheme()` / `Storefront.setColorScheme('dark'|'light')` flip the root class, set `color-scheme`, persist the cookie fire-and-forget, and dispatch a `storefront:color-scheme` event.

#### Light/dark logos & images

Render both variants and swap them with CSS keyed on the root class — never with a `dark:` utility (see the caveat below). A logo without a dark variant simply omits the `--light` marker and shows in both schemes:

```blade
@if(!empty($store['logo']))
    <img src="{{ $store['logo'] }}" class="storefront-logo {{ !empty($store['logo_dark']) ? 'storefront-logo--light' : '' }}" alt="{{ $store['name'] }}">
    @if(!empty($store['logo_dark']))
        <img src="{{ $store['logo_dark'] }}" class="storefront-logo storefront-logo--dark" alt="{{ $store['name'] }}">
    @endif
@endif
```

```css
.storefront-logo--dark { display: none; }
:root.dark .storefront-logo--light { display: none; }
:root.dark .storefront-logo--dark  { display: block; }
```

`$store['logo_dark']` is the admin's dark-mode logo (null when unset). The login background is pre-resolved per scheme as `$store['login_background']` (the raw `login_background_image` / `login_background_image_dark` are also available).

#### Providing dark-surface fallbacks

The platform dark defaults are already usable. A theme can provide its own
values by redeclaring the **same `--brand-*` tokens** under `:root.dark` in
`assets/css/storefront.css` (served live — no rebuild). As in light mode
(§11.8.1), wrap them in `@layer theme-defaults` when they are fallbacks the
store owner's Appearance settings should still override, or declare them
unlayered when the theme owns the dark palette outright:

```css
@layer theme-defaults {
    :root.dark {
        --brand-color-surface-page: #0a0a0f;
        --brand-color-surface-card: #14141c;
        --brand-color-headings:     #f5f5f5;
        --brand-color-body:         #d1d1d6;
    }
}

/* Not an Appearance token — always unlayered. */
:root.dark {
    color-scheme: dark;                       /* native controls + scrollbars */
}
```

The tokens in §11.6 (headings / body / placeholder), §11.7 (page chrome, borders, status subtles, disabled, inputs) and §11.8 (tooltip / backdrop) all have meaningful dark defaults — override only the ones you want to change.

#### Subtle brand tints in dark mode

The `50`–`400` stops are the *subtle* end of a ramp: `bg-primary-50` is the
standard fill for a badge, a selected row, or a `hover:` state on a ghost
button. Appearance builds them by mixing the base colour toward the **page
surface of that scheme** — toward white for `:root`, toward the dark page
surface for `:root.dark` — so a subtle fill stays subtle in both. Tint them
toward white yourself and dark mode gets a glaring near-white block that is
brighter than the body text.

So if your theme declares its own ramp and you support dark mode, give
`:root.dark` a set of dark-anchored light stops rather than reusing the light
ones:

```css
:root {
    --brand-color-primary-50:  #fbf9ec;   /* base mixed toward white */
    --brand-color-primary-100: #f6f1cf;
}

:root.dark {
    --brand-color-primary-50:  #1d1e1a;   /* base mixed toward the dark page */
    --brand-color-primary-100: #343222;
}
```

Leaving the light stops out of `:root.dark` entirely is also fine — Appearance
emits a dark-anchored ramp of its own, and `:root.dark` outranks a bare
`:root`, so the tenant's dark tints win over your light ones.

#### ⚠️ Do not add new `dark:` utility classes

`base.css` is a prebuilt artifact that themes **cannot** rebuild on upload, and only a tiny set of `dark:` variants is compiled into it. A `dark:` class that isn't already compiled silently does nothing. **Re-skin through the token cascade instead** (it covers surfaces, text, borders and inputs for free), and for anything element-specific (logo / toggle swaps, fixed chrome) write a plain `:root.dark <selector>` rule in your own stylesheet, which is served live.

#### Testing checklist

- [ ] Toggle works with JavaScript **off** (full-page POST returns to the same page) and **on** (flips live, no reload).
- [ ] First paint matches the saved cookie on reload (no flash), and a first visit honors the OS `prefers-color-scheme`.
- [ ] Every page (home, listing, product, cart, checkout, account, login, 404 / 5xx) is legible in both schemes — surfaces, text, inputs, borders, focus rings.
- [ ] The dark logo (and login background) appear only in dark mode; a store with no dark logo still shows its light one.

### 11.11 Recommended token file (skeleton)

A typical `assets/css/storefront.css` for a custom theme. This file loads after
the tenant Appearance block, so the choice of `:root` vs `@layer theme-defaults`
decides who owns each token (§11.8.1). The skeleton below owns the brand
identity and leaves the neutral surfaces to the store owner:

```css
/* Brand identity — owned by the theme, Appearance cannot override it. */
:root {
    /* Fonts */
    --font-primary:   "Playfair Display", Georgia, serif;                     /* headings */
    --font-secondary: "Inter", -apple-system, BlinkMacSystemFont, sans-serif; /* body */

    /* Geometry */
    --brand-radius: 0.75rem;

    /* Primary brand color (regenerate the full scale for best results) */
    --brand-color-primary-50:  #fff5eb;
    --brand-color-primary-100: #ffe1c2;
    --brand-color-primary-200: #ffc285;
    --brand-color-primary-300: #ff9e47;
    --brand-color-primary-400: #ff7e1a;
    --brand-color-primary-500: #ff6a00;
    --brand-color-primary-600: #cc5500;
    --brand-color-primary-700: #993f00;
    --brand-color-primary-800: #662a00;

    /* Owning the ramp means owning the label colour on top of it (§11.5). */
    --brand-color-primary-content: #ffffff;
}

/* Subtle stops re-mixed toward the dark page, so hovers and badges stay
 * subtle instead of glowing near-white (§11.10). */
:root.dark {
    --brand-color-primary-50:  #241a10;
    --brand-color-primary-100: #3a2716;
}

/* Defaults — the store owner can still change these from Appearance. */
@layer theme-defaults {
    :root {
        --brand-color-surface-page: #fafafa;
    }

    :root.dark {
        --brand-color-surface-page: #14131a;
        --brand-color-surface-card: #1c1b24;
    }
}
```

> Tip: when you change a `*-500`, also update the surrounding shades. Many subtle surface tokens reference `*-50`, `*-200`, and `*-500` of the same family.

---
