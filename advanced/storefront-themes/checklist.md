---
title: Author checklist
description: Override strategy and the pre-upload author checklist.
---

## 12. Override strategy

A theme only needs to ship the files it overrides. Anything missing falls back to the bundled default theme.

Typical minimal override set:

```
theme.json
pages/product.blade.php          # change just the product page
assets/css/storefront.css        # override CSS variables
```

When overriding a page, include the same `@extends(...)` / `@section(...)` blocks as the default version so layout slots stay connected.

---

## 13. Quick author checklist

Before zipping:

- [ ] `theme.json` is at the zip root with `name`, `slug`, `version`
- [ ] Every blade path matches the canonical surface (or `pages/<slug>.blade.php`)
- [ ] No `@php`, `@inject`, `@eval`, `<?php`, `<?=`, backticks, or `$__env`
- [ ] No dynamic `@include($x)` / `@extends($x)` — string literals only
- [ ] No Laravel helpers (`app`, `request`, `config`, `env`, `session`, `cookie`, `auth`)
- [ ] No facades (`Auth::`, `DB::`, `Cache::`, `Storage::`, …)
- [ ] No forbidden functions (`eval`, `exec`, `file_*`, `unserialize`, `base64_decode`, …)
- [ ] Asset files use only whitelisted extensions per folder
- [ ] All derived values computed inline via `data_get(...) ?? ...` and ternaries, never `@php`
- [ ] Every user-facing string is wrapped in `@t(...)` / `t(...)`, **or** lives in a per-locale page under `pages/<locale>/...`
- [ ] Every date / datetime is rendered via `@formatDate(...)` (no raw Carbon echo, no `date()` calls)
- [ ] Every monetary value is rendered via `@formatCurrency(...)` (no hardcoded currency symbol, no manual `number_format`)
- [ ] Every numeric value (counts, weights, stock) is rendered via `@formatNumber(...)`
- [ ] Product images are read via `resolved_main_media` (with `main_media` as the serialized fallback) and wrapped in `@storefrontImage(...)` (§9.11) — never read the `mainMedia` relation directly (it's a has-many collection, so `mainMedia.media_url` is always `null`). Listing and detail must agree on the main image; product detail uses `$galleryImages` and shows thumbnail rails when there is more than one image; in table mode, variant-row thumbnails link to `?variant=<id>`
- [ ] Store info & capability flags read from `$store['key']` — the single source; injected globals (`$me`, `$canSeePrices`, `$canAddToCart`, `$store`, `$cartCount`, `$cartTotals`) read directly, no `?? default`
- [ ] Prices are gated on `$canSeePrices` and add-to-cart forms on `$canAddToCart` (§9.6); cart rewards read `$cartProgress` and honour each rule's own `show_progress_bar` (no tenant-wide toggle)
- [ ] Every applicable flag in the §9.6 *Feature-by-feature compliance guide* is respected exactly like the default theme (same file, same guard) — unless the requester explicitly said to skip that specific feature for this theme
- [ ] Submit controls are real `<button type="submit">` / `<input type="submit">` **inside** their form with an accessible label, so the automatic loading spinner (§9.9) can find and mark them; busy hooks (`.storefront-busy`, `[data-storefront-progress]`) are left intact
- [ ] Custom inline-script async actions drive `Storefront.setBusy(el)` / `Storefront.progress` for loading feedback, wrapped in `try` / `finally` and guarded with `window.Storefront?.` (§9.9)
- [ ] Every actionable element (buttons, links, `<form>`s + submit controls, `tel:` / `mailto:` links) has a stable, unique, descriptive `id` so Google Tag Manager can track interactions the platform doesn't emit as GA4 events (§9.13)
- [ ] Per-locale page folders use lowercased BCP-47 tags only (`pages/de-de/...`, not `pages/de-DE/...`)
- [ ] If the theme ships `pages/not-found.blade.php`, it renders without any extra view data (only platform-injected globals) and never performs heavy queries
- [ ] If the theme ships `pages/error.blade.php`, every reference to `$errorDebug` is wrapped in `@isset($errorDebug)` (production never exposes it); the page never queries the DB or hits external services; `$errorReference` is surfaced for support correlation
- [ ] Styling uses **Tailwind utility classes** first; custom CSS only where a utility composition won't do
- [ ] Colors / spacing / typography reference **design tokens** (`text-primary-500`, `bg-surface-card`, `font-primary`) — no hardcoded hex, px font sizes, or font-family strings
- [ ] Custom fonts are **loaded** (Google Fonts `<link>` / `@import`, or self-hosted `@font-face` from `assets/fonts/`) **and** wired to `--font-primary` / `--font-secondary` with a system fallback in the stack (§11.1) — EU storefronts self-host to stay GDPR-safe
- [ ] Brand customization done by overriding `--brand-*` variables in `assets/css/storefront.css`, not by re-declaring `--color-*` / `--text-*` directly
- [ ] Every `--brand-*` / `--font-*` declaration is a deliberate ownership choice (§11.8.1): plain `:root` where the theme owns the token, `@layer theme-defaults` where Store setup → Appearance must still be able to override it — and never `!important` or a boosted selector to force one
- [ ] Text on a solid brand surface uses `text-primary-content` / `text-secondary-content`, never `text-neutral-white` (§11.5) — and a theme that declares its own `--brand-color-primary-*` ramp declares `--brand-color-primary-content` with it
- [ ] A theme-owned ramp re-mixes its `50`–`400` stops toward the dark page surface under `:root.dark` (§11.10), so badges and `hover:` fills stay subtle in dark mode
- [ ] Hover / pressed states use `hover:bg-surface-hover` / `bg-surface-active` (§11.7), and selected / brand-marked states use `bg-primary-subtle` (§11.5) — never an opaque `bg-surface-*` or `bg-primary-50`, which cannot adapt to the page, the card and the header at once
- [ ] No `@tailwind` directive, CDN script, or duplicate Tailwind import — `base.css` is already loaded by the layout
