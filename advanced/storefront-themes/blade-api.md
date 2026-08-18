---
title: Blade API
description: The allowed authoring toolkit: theme directives and helper functions.
---

<Info>
This page also ships inside the default theme download under `docs/01-blade-api.md`, so offline and AI-assisted authors have the same contract locally. This online version is always the latest.
</Info>

## 9. Allowed authoring toolkit

Use **only** the following to build themes:

### Blade control flow
- `@if` / `@elseif` / `@else` / `@endif`
- `@foreach` / `@forelse` / `@for` / `@while`
- `@isset` / `@empty`
- `@section('name') ... @show` and `@section('name') ... @endsection`
- `@yield('name')`
- `@extends('layouts.shop')` (literal string only)
- `@include('components.price', [...])` (literal string only)
- `@stack` / `@push` / `@prepend`

### Output
- `{{ $value }}` — escaped
- `{!! $value !!}` — unescaped (use sparingly, for trusted HTML only)
- `{{-- comment --}}`

### Allowed Blade directives (theme-specific)

In addition to standard Blade control flow above, the platform registers these theme-only directives:

| Directive                                | Mirror helper                 | Purpose                                                                                |
| ---------------------------------------- | ----------------------------- | -------------------------------------------------------------------------------------- |
| `@t('English key')`                      | `t('English key')`            | Translate via Settings Hub (see §9.1)                                                |
| `@t('Up to %d rows', $max)`              | `t('Up to %d rows', $max)`    | Same, with printf-style values injected after the lookup (see §9.1)                  |
| `@routeUrl('store.home', [...], $locale?)` | `routeUrl(...)`             | Build a locale-aware route URL; defaults to the active locale, pass `$locale` to target another |
| `@themeAsset('img/logo.png')`            | —                             | Asset URL relative to the active theme's `assets/` folder                              |
| `@storefrontAsset('storefront.css')`     | —                             | Asset URL for a published platform asset (cache-busted)                                   |
| `@storefrontImage('url', w?, h?, q?)`    | —                             | Bunny-optimised image URL — sizing params on-CDN, pass-through off-CDN (see §9.11)      |
| `@formatCurrency($amount, $currency?)`   | `formatCurrency(...)`         | Locale + currency aware money formatting (see §9.4)                                  |
| `@formatNumber($value, $maxFraction?)`   | `formatNumber(...)`           | Locale-aware decimal formatting (see §9.4)                                           |
| `@formatDate($value, $format?)`          | `formatDate(...)`             | Locale-aware date / time formatting (see §9.3)                                       |
| `@storefrontSection('cart-summary')`     | —                             | Render an AJAX-refreshable section in place (see §9.7)                                |
| `@storefrontSlot('product.detail.meta', ['context' => …])` | — | Render a named slot: optional-module contributions **and** owner-authored CMS content. Optional config object declares slot context for the Theme Editor (see §9.16). Renders nothing when empty. |
| `@storefrontScripts`                     | —                             | Emit the storefront JS runtime once near `</body>` — enables cart AJAX (see §9.7)     |
| `@storefrontAuthToken`                   | —                             | Short-lived (1h) `x-auth-token` for the logged-in customer (empty for guests) — inits a first-party widget's `api_key` (see §9.14). ⚠️ The only sanctioned credential exposure. |
| `@storefrontSeo`                         | —                             | Emit the SEO head — robots, canonical, hreflang, Open Graph, Twitter Card & JSON-LD (see §9.10) |
| `@storefrontAnalytics`                   | —                             | Emit the consent-gated analytics loader — GTM / GA4 / Clarity — in `<head>` (see §9.13) |
| `@storefrontColorScheme`                 | —                             | Emit the current light/dark scheme onto `<html>` before stylesheets load (reads `$colorScheme`; must precede theme CSS). See §11.10 |
| `@fetch('url', [...], 'var')`            | —                             | **Server-side HTTP fetch** — assigns the decoded response to `$var` (see §9.12). ⚠️ Read the data-exposure rule first. |

### Allowed helper functions (use inside expressions where directives can't reach)

| Helper                                       | Purpose                                                                                |
| -------------------------------------------- | -------------------------------------------------------------------------------------- |
| `data_get($subject, 'dot.path', $default)`   | Primary tool for reading from view data                                                |
| `t('English key')`                           | Same as `@t` — use inside `@include([...])` arrays, `@section('title', t('Shop'))`     |
| `t('English key %d', $value, …)`             | Same as `@t` with values — printf specifiers filled after the lookup (see §9.1)       |
| `formatCurrency($amount, $currency?)`        | Same as `@formatCurrency`                                                              |
| `formatNumber($value, $maxFraction?)`        | Same as `@formatNumber`                                                                |
| `formatDate($value, $format?)`               | Same as `@formatDate`                                                                  |
| `routeUrl($name, $params?, $locale?)`        | Same as `@routeUrl` — locale-aware named route URL (pass `$locale` to target another language) |
| `localeUrl($locale, $route?, $params?)`      | Current page URL in a different locale — for locale switchers and hreflang tags        |
| `canonicalUrl()`                             | Canonical URL of the current page in the active locale                                 |
| `orderStatusLabel($status)`                  | Localised, human-readable label for an order status (e.g. `completed` → "Completed"). Use on order lists/detail (see §10). |
| `orderStatusTone($status)`                   | Semantic tone token for an order status (`success`/`info`/`warning`/`error`/…) — pair with `orderStatusLabel()` to colour a status badge. |
| Native PHP operators: `??`, `?:`, `==`, `&&`, ternaries                                                                                   |

### Computing derived values without `@php`

Since `@php` is forbidden, derive values inline in directive arguments:

```blade
@include('components.price', [
    'amount'    => data_get($product, 'finalPrice.price')
        ?? data_get($product, 'specialPrice.price')
        ?? data_get($product, 'price.price')
        ?? 0,
    'compareAt' => data_get($product, 'specialPrice.price') !== null
        ? data_get($product, 'price.price')
        : null,
])
```

---
