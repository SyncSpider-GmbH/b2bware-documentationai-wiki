---
title: Blade API
description: The allowed authoring toolkit: theme directives and helper functions.
---

## 9. Allowed authoring toolkit

Use **only** the following to build themes:

### Blade control flow
- `@if` / `@elseif` / `@else` / `@endif`
- `@foreach` / `@forelse` / `@for` / `@while`
- `@isset` / `@empty`
- `@section('name') ... @show` and `@section('name') ... @endsection`
- `@parent` inside an overriding `@section` — keep the default content and add to it
- `@yield('name')`
- `@extends('layouts.shop')` (literal string only) — for a fully custom page
- `@extends('default::pages.cart')` (literal string only) — reuse a default page and override single sections (see §9.0)
- `@include('components.price', [...])` (literal string only)
- `@stack` / `@push` / `@prepend`

### 9.0 Extending a default page (section overrides)

The platform default theme is always available under the `default::` prefix. Instead of copying a whole page, ship a thin page that extends the default one and overrides only the sections you change. Everything you do not override keeps coming from the default theme, including future fixes and features.

```blade
{{-- pages/cart.blade.php in your theme --}}
@extends('default::pages.cart')

@section('cart.header')
    <h1 class="text-3xl font-semibold">@t('Your order basket')</h1>
@endsection

@section('cart.sidebar')
    @parent
    <p class="text-sm">@t('Free delivery from 200 EUR')</p>
@endsection
```

- Use `@section('name') … @endsection` in your file. `@parent` renders the default content at that spot.
- Copying the full page file instead (`@extends('layouts.shop')` plus everything else) works, but that page then stops receiving default-theme updates.
- Header and footer sections can be overridden from any page that extends a default page. To change them on every page you still need your own `partials/header.blade.php` / `partials/footer.blade.php`.

Section names you can override:

| File | Sections |
| --- | --- |
| `pages/cart` | `cart.header`, `cart.main` (contains `cart.actions`), `cart.sidebar` |
| `pages/checkout` | `checkout.header`, `checkout.main`, `checkout.summary` |
| `pages/favorites` | `account.nav`, `account.main` (contains `favorites.header`, `favorites.lists`, `favorites.grid`) |
| `pages/account/index`, `profile`, `orders`, `order`, `api-keys`, `catalog-export`, `quick-order` | `account.nav`, `account.main` |
| `pages/account/shipping-addresses`, `billing-addresses` (via `partials/account-addresses-page`) | `account.nav`, `account.main` (contains `addresses.list`, `addresses.company`) |
| `pages/login`, `register`, `forgot-password`, `reset-password`, `verify-email` | `<page>.brand` (side panel), `<page>.form` — e.g. `login.brand`, `reset-password.form` |
| `pages/products` | `hero`, `header`, `toolbar`, `filters`, `listing`, `pagination` |
| `pages/categories` | `hero`, `listing` |
| `pages/category` | `hero`, `category.header`, `category.children`, `category.products` |
| `pages/guest-order` | `guest-order.header`, `guest-order.summary`, `guest-order.items`, `guest-order.addresses`, `guest-order.note` |
| `pages/proposal-preview` | `proposal.header`, `proposal.items`, `proposal.products`, `proposal.summary` |
| `pages/customer-selection` | `customer-selection.search`, `customer-selection.list` |
| `pages/error`, `pages/not-found` | `<page>.message`, `<page>.actions` — e.g. `not-found.actions` |
| `pages/product` (via `partials/product-details`) | `gallery`, `sku`, `availability`, `price`, `tier-highlight`, `tier-prices`, `short-description`, `variants`, `variant-table`, `purchase`, `tabs`, `related-products` |
| `partials/header` | `header.banner`, `header.brand`, `header.search`, `header.search-mobile`, `header.nav`, `header.actions` |
| `partials/footer` | `footer.brand`, `footer.shop`, `footer.account`, `footer.support`, `footer.copyright` |
| `layouts/shop` | `breadcrumbs` |

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
| `@storefrontImage('url', w?, h?, q?, aspect?)` | —                      | Optimised image URL — Bunny / desk sizing params on-CDN, pass-through off-CDN (see §9.11; **required** for every `media_url`) |
| `@formatCurrency($amount, $currency?)`   | `formatCurrency(...)`         | Locale + currency aware money formatting (see §9.4)                                  |
| `@formatNumber($value, $maxFraction?)`   | `formatNumber(...)`           | Locale-aware decimal formatting (see §9.4)                                           |
| `@formatDate($value, $format?)`          | `formatDate(...)`             | Locale-aware date / time formatting (see §9.3)                                       |
| `@storefrontSection('cart-summary')`     | —                             | Render an AJAX-refreshable section in place (see §9.7)                                |
| `@storefrontSlot('product.detail.meta', ['context' => …])` | — | Render a named slot: optional-module contributions **and** owner-authored CMS content. Optional config object declares slot context for the Theme Editor (see §9.16). Renders nothing when empty. |
| `@storefrontScripts`                     | —                             | Emit the storefront JS runtime once near `</body>` — enables cart AJAX (see §9.7)     |
| `@storefrontCaptcha`                     | —                             | Place the tenant's CAPTCHA widget at this exact spot inside a `@storefrontForm`. Optional — a protected form that omits it gets the widget injected just before `</form>` (see `forms.md`) |
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
| `storefront_countries()`                     | The platform's canonical country list, sorted by name, for building a country `<select>` in address forms. Each row is `['name','iso2','iso3']`. |
| `storefront_country_name($value)`            | Resolve a stored/submitted country value (name, ISO2 or ISO3) to its canonical name — use to preselect the matching `<option>`. |
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
