---
title: Hard rules
description: Archive layout, canonical file surface, and the forbidden Blade/PHP the upload validator hard-rejects.
---

<Info>
This page also ships inside the default theme download under `docs/00-hard-rules.md`, so offline and AI-assisted authors have the same contract locally. This online version is always the latest.
</Info>

## 1. Archive layout

A theme zip must contain **`theme.json` at the root**. A single top-level wrapper folder is unwrapped automatically, and OS/editor junk (`__MACOSX/`, `.DS_Store`, AppleDouble `._*`, `.git/`, …) is stripped — so a zip made with macOS Finder "Compress" uploads as-is.

Theme top-level entries (everything else is ignored, not rejected):

```
theme.json        (required)
preview.png       (optional)
README.md         (optional)
readme.md         (optional)
rules.md          (optional, thin stub — points at docs/)
docs/             (optional, this authoring guide; *.md only)
layouts/
partials/
components/
pages/
modules/
assets/
```

> `docs/` ships **with** the default theme and is kept when you re-upload, but it is
> documentation only — it is never rendered. The authoritative, always-current version is
> online (see the header of each doc page). Only `*.md` files are kept under `docs/`.

### `theme.json` shape

```json
{
  "name": "My Theme",
  "slug": "my-theme",
  "author": "Your Name",
  "version": "1.0.0",
  "description": "Short description.",
  "license": "Proprietary"
}
```

---

## 2. Canonical file surface

Each blade file must either match one of the canonical paths below **or** be a custom page at `pages/<slug>.blade.php` where `<slug>` is `[a-z0-9][a-z0-9-]*`. Nested folders under `pages/` are forbidden (the only exception is the hard-coded `pages/account/...` set).

### Layouts (`layouts/`)
- `shop.blade.php`
- `auth.blade.php`

> The default theme ships only these two layouts. **Uploaded themes may add their own
> `layouts/<slug>.blade.php`** (single lowercase-dash segment, no nested folders) and reference them
> from pages with a string-literal `@extends`. Custom layouts are validated like any other theme file.

> Some platform pages render as a **standalone document** without the shop chrome — currently the
> anonymous public proposal share page (`/​{locale}/proposals/public/{token}`) when the proposal can
> be ordered directly. Those pages receive `$hideChrome = true`; the default `shop.blade.php` wraps
> its header / breadcrumbs / footer / added-to-cart includes in `@unless($hideChrome ?? false)`.

> **Admin-authored rich text.** Blocks rendered raw from admin content (proposal / group
> descriptions, etc.) are wrapped in `.storefront-richtext`. The platform stylesheet (`base.css`)
> ships typographic defaults for that class (heading scale, paragraph spacing, links, lists,
> centered `figure` images) and maps the editor-emitted `.text-brand-primary` span class onto the
> store's primary color token. Uploaded themes may override any of it with their own CSS.
> Honour the same flag in a custom shop layout, or the share page renders with full store chrome.

### Partials (`partials/`)
- `header.blade.php`
- `footer.blade.php`
- `nav.blade.php`
- `mini-cart.blade.php`
- `locale-switcher.blade.php`
- `breadcrumbs.blade.php`
- `cart-line-items.blade.php` &mdash; cart line rows + empty state (AJAX section, §9.7)
- `cart-discounts.blade.php` &mdash; coupon + applied rules (AJAX section, §9.7)
- `cart-summary.blade.php` &mdash; cart totals (AJAX section, §9.7)
- `cart-rewards.blade.php` &mdash; reward progress bars (AJAX section, §9.7)
- `checkout-summary.blade.php` &mdash; checkout coupon + totals (AJAX section, §9.7)
- `account-nav.blade.php` &mdash; account sidebar navigation; pass `active` (dashboard, profile, orders, addresses, favorites) to highlight the active item
- `account-address-form.blade.php` &mdash; address field group (name, street, city, country, phone); included inside both the account address modals and the inline checkout address forms; pass `address` (existing object or null) and `prefix` (shipping or billing)
- `account-addresses-page.blade.php` &mdash; full addresses page layout (address cards, add/edit modals); used by both `account/shipping-addresses` and `account/billing-addresses`; pass the form names and address collections documented at the top of the partial
- `checkout-address-option.blade.php` &mdash; selectable address card in the checkout billing/delivery pickers; pass `address`, `field` (`billing_address_id` | `shipping_address_id`), `selectedId` and `required`
- `checkout-address-summary.blade.php` &mdash; compact address row inside the checkout "Manage addresses" modals; pass `address` and `defaultForm`
- `catalog-export-fields.blade.php` &mdash; shared column switches + native product filters for the catalog-export page (only rendered when `$store['catalog_export_enabled']`)
- `catalog-export-preview.blade.php` &mdash; live catalog-export preview table (AJAX section, §9.7; only rendered when `$store['catalog_export_enabled']`)
- `product-details.blade.php` &mdash; the whole product-page body as a single AJAX-refreshable section (`product-details`, §9.7) so the variant picker can re-render it server-side
- `added-to-cart-modal.blade.php` &mdash; the added-to-cart confirmation `<dialog>`; included from `shop.blade.php`. Override for a drawer/toast, or omit the `@include` to suppress it (§9.7)

> The default theme ships these canonical partials. **Uploaded themes may add their own
> `partials/<slug>.blade.php`** (single lowercase-dash segment, no nested folders) to DRY out
> shared UI patterns. Custom partials are validated like any other theme file.

### Components (`components/`)
- `product-card.blade.php`
- `product-gallery.blade.php`
- `add-to-cart-button.blade.php`
- `price.blade.php`
- `stock-badge.blade.php`
- `quantity-selector.blade.php`
- `banner.blade.php` &mdash; page-level flash message. Pass `type` (`success` | `info` | `warning` | `error`; anything else renders as info), `message` (the already-localized string; renders nothing when empty) and optionally `class` for context-specific spacing. Every `$messages` banner in the default theme goes through it &mdash; see §9.6. For **per-field validation errors** use `@storefrontError` instead.
- `button.blade.php`
- `pagination.blade.php`
- `empty-state.blade.php`

> The default theme ships these canonical components. **Uploaded themes may add their own
> `components/<slug>.blade.php`** (single lowercase-dash segment, no nested folders) to DRY out
> theme-specific UI patterns. Custom components are validated like any other theme file.

### Fixed pages (`pages/`)
- `products.blade.php`, `product.blade.php`
- `categories.blade.php`, `category.blade.php`
- `cart.blade.php`, `checkout.blade.php`
- `guest-order.blade.php` — order confirmation for guest checkouts; access protected by a signed URL so it is bookmarkable without login. Variables: `$order` (Orders model or null), `$orderId` (string), `$orderItems` (Collection), `$orderTotals` (array with keys `subtotal`, `shipping`, `discount`, `tax`, `grand_total`).
- `login.blade.php`, `register.blade.php`, `logout.blade.php`
- `forgot-password.blade.php`, `reset-password.blade.php`, `verify-email.blade.php`
- `customer-selection.blade.php`, `favorites.blade.php`
- `proposal-preview.blade.php` &mdash; proposal review / accept page; also served standalone (`$hideChrome = true`) as the anonymous public share page. See the page recipe in §10 for its view-data contract.
- `not-found.blade.php` &mdash; rendered for every 404 on a storefront host (unknown URL, draft/private product, missing category, etc.). See §2.1.
- `error.blade.php` &mdash; rendered for every uncaught server error (HTTP 5xx) on a storefront host. See §2.2.
- `account/index.blade.php`, `account/profile.blade.php`
- `account/shipping-addresses.blade.php`
- `account/billing-addresses.blade.php`
- `account/orders.blade.php`, `account/order.blade.php`
- `account/quick-order.blade.php` &mdash; Quick Order (SKU autocomplete + CSV bulk add). Rendered **only when the tenant enables it** (`$store['quick_order_enabled']`, defaults off); the account-nav link is gated on the same flag. When disabled the routes 404, so never link to it unconditionally.
- `account/catalog-export.blade.php` &mdash; only reachable when `$store['catalog_export_enabled']`; a single config surface (draggable column switches + native product filters + live preview table) that generates the customer's single stored export (a frozen snapshot), which they can then download locally or share via a tokenized public link.
- `account/api-keys.blade.php` &mdash; always reachable (no settings flag); lets the customer create and revoke their own API keys for accessing the API programmatically as themselves via the `x-auth-token` header. The plaintext token is only ever available once, right after creation — session-flashed by the controller and passed to the view as `$newApiKeyToken`, never persisted or re-shown after that single render.

### Custom pages
- `pages/my-custom-page.blade.php` — must be a single segment, lowercase, dash-separated.

### Module extension overrides (`modules/`)
- `modules/<module-slug>/<view>.blade.php` — an **optional** folder. Installed platform modules can inject their own markup into the storefront at named **extension slots** (§9.16) — e.g. a "customer SKU" module adds the customer's own SKU under the product SKU. Each module ships its own blade for that; you only need this folder if you want to **restyle** a module's contribution. Drop a file at `modules/<module-slug>/<view>.blade.php` (both segments lowercase, dash-separated, one nested level) and it overrides that module's default blade. You never create slots or register modules — you only override what a module already renders. See §9.16 for the slot list and the variables each override receives.

---

## 2.1 The not-found (404) page

Every storefront 404 — unknown URL, deleted product, product whose `status` is not `public`, missing category, malformed locale slug — is rendered through **`pages/not-found.blade.php`** with HTTP status `404`. Themes do **not** need to throw or handle 404s themselves; the platform catches `NotFoundHttpException` for any request on a tenant host and renders the theme's not-found page automatically.

- The page receives **no extra view data** beyond the global variables injected by the platform (`$locale`, `$me`, `$cart`, `$availableLocales`, …). Anything else (a search box, recommended products, a recent-views carousel) must be self-contained or read from those globals.
- The locale override rules (see §9.1, Strategy B) apply normally: `pages/de-de/not-found.blade.php` overrides the German 404 page only.
- JSON / API requests are **not** routed through this template — they get the platform's default JSON 404 body so storefront AJAX endpoints behave predictably.
- Keep the page lightweight (no heavy DB lookups, no external API calls). A 404 page is hit by crawlers and broken-link traffic; it must render fast and never throw.

Minimal example:

```blade
@extends('layouts.shop')

@section('title', t('Page not found'))

@section('content')
    <div class="page page--not-found flex flex-col items-center text-center gap-6 py-16">
        <p class="font-primary text-7xl font-bold text-primary">404</p>
        <h1 class="text-2xl text-headings">@t('Page not found')</h1>
        <p class="text-body">@t('The page you are looking for does not exist.')</p>
        <a href="@routeUrl('store.home')" class="bg-primary text-primary-content rounded px-4 py-2 no-underline">
            @t('Back to home')
        </a>
    </div>
@endsection
```

---

## 2.2 The error (5xx) page

Every uncaught server exception on a storefront host is rendered through **`pages/error.blade.php`** with the appropriate 5xx HTTP status (defaulting to `500`). The full PHP exception &mdash; class, message, stack trace, originating URL &mdash; is **always written to the platform log** with a short reference id, regardless of `APP_DEBUG`.

**What the template receives**:

| Variable          | Type                  | When set                                                                                              |
| ----------------- | --------------------- | ----------------------------------------------------------------------------------------------------- |
| `$errorReference` | `string` (12 hex chars) | Always. Show this to the visitor so support can correlate it with the server log.                   |
| `$errorStatus`    | `int` (e.g. `500`, `503`) | Always. Display in the heading.                                                                  |
| `$errorDebug`     | `array` or `null`     | **Only** when `APP_DEBUG=true`. Keys: `class`, `message`, `file`, `line`, `trace`. **Never assume it's set in production.** Always wrap in `@isset($errorDebug)`. |

Globals from the platform (`$locale`, `$me`, `$cart`, `$availableLocales`) are still injected.

### Hard rules for the error page

- **Never echo `$errorDebug` outside an `@isset($errorDebug)` guard.** In production this variable is `null` and exposing it would leak server internals.
- **Never render `$e`, `$exception`, or any raw exception object.** Only the keys listed above are available, and only when debug mode is on.
- **Keep the page self-contained.** No DB queries, no API calls, no template lookups that could themselves fail &mdash; an error page that throws is a redirect loop waiting to happen.
- **No links to routes that require authentication or a resolved tenant context** beyond what's globally injected.
- A user-visible reference id (`$errorReference`) plus a **copy button** is the recommended UX &mdash; matches the Sentry / Shopify / Shopware pattern ("share this id with support").

### Custom client-side JavaScript

When a blade needs custom client JS, write it as a **native ES module inlined in the same blade** as the markup it wires up &mdash; a `<script type="module">` block. Keep it colocated with its consumer: never split a feature's script into a separate `assets/js/*.js` file, and duplicate a small module across pages rather than sharing one (just like partials and components). `type="module"` is module-scoped and deferred, so the code runs after the DOM is parsed with no global leakage &mdash; **no IIFE, no `'use strict'`, no `DOMContentLoaded` wrapper, no `var`**.

Use current-baseline browser features (anything supported by browsers from roughly the last two years): `const` / `let`, arrow functions, `for...of`, spread / `Array.from`, optional chaining `?.`, nullish coalescing `??`, `el.dataset`, `classList.toggle(name, force)`, `el.form.requestSubmit()`, `navigator.clipboard`, template literals. **Never** reach for legacy hacks: no IIFEs, no `var`, no inline `on*=` attribute handlers (bind `addEventListener` to a `data-*` hook instead), no `document.execCommand`, no `javascript:` URLs, and no jQuery / Alpine / framework. Every behaviour must still degrade gracefully with JavaScript off.

> Template literals (backticks) are safe inside an inline `<script>`, but never write a bare `app(`, `request(`, `config(`, `env(`, `session(`, `cookie(`, or `auth(` call in inline JS &mdash; the safety scanner's helper denylist matches those names followed by `(` anywhere in the file. Use `window.`-qualified APIs (e.g. `window.confirm(...)`).

The platform ships **two** standalone JS files, both platform assets (not theme JS) that you never inline or fork: the cart AJAX runtime (`resources/js/storefront.js`, loaded once via `@storefrontScripts`), and &mdash; only for tenants who enabled analytics &mdash; the consent + tracking runtime loaded **on demand** by `@storefrontAnalytics` (§9.13). You still never add your own standalone `assets/js/*.js` file; keep theme JS inline per the rule above.

### Copy-to-clipboard pattern (reference)

For a copy-to-reference-id button, inline a `<script type="module">` block in the same blade as the markup it wires up. See [`pages/error.blade.php`](pages/error.blade.php) for the reference implementation: it auto-binds every element with `data-copy-target="<id>"` and copies via `navigator.clipboard` (no legacy fallback &mdash; copy silently no-ops on non-secure / ancient browsers, and the reference id stays hand-selectable).

```blade
<code id="my-payload" class="select-all">{{ $errorReference }}</code>
<button type="button"
        data-copy-target="my-payload"
        data-copy-label-default="{{ t('Copy') }}"
        data-copy-label-copied="{{ t('Copied') }}">
    @t('Copy')
</button>

<script type="module">
    // Inline; keep the JS that wires this button in the same blade as the button.
    for (const btn of document.querySelectorAll('[data-copy-target]')) {
        btn.addEventListener('click', async () => {
            const target = document.getElementById(btn.dataset.copyTarget);
            if (!target || !navigator.clipboard) return;
            try {
                await navigator.clipboard.writeText((target.value ?? target.textContent ?? '').trim());
            } catch {
                return;
            }
            const copied = btn.dataset.copyLabelCopied;
            if (!copied) return;
            const original = btn.dataset.copyLabelDefault ?? btn.textContent;
            btn.textContent = copied;
            setTimeout(() => { btn.textContent = original; }, 2000);
        });
    }
</script>
```

### Minimal example

```blade
@extends('layouts.shop')

@section('title', t('Something went wrong'))

@section('content')
    <div class="page page--error flex flex-col items-center text-center gap-6 py-16">
        <p class="font-primary text-7xl font-bold text-error">{{ $errorStatus ?? 500 }}</p>
        <h1 class="text-2xl text-headings">@t('Something went wrong')</h1>
        <p class="text-body">@t('An unexpected error occurred. Our team has been notified.')</p>

        @isset($errorReference)
            <div class="bg-surface-card border rounded p-4">
                <p class="text-sm text-body">@t('If you need help, share this reference with support.')</p>
                <code id="err-ref" class="select-all">{{ $errorReference }}</code>
                <button type="button" data-copy-target="err-ref"
                        data-copy-label-default="{{ t('Copy') }}"
                        data-copy-label-copied="{{ t('Copied') }}">@t('Copy')</button>
            </div>
        @endisset

        @isset($errorDebug)
            <details class="bg-surface-warning-subtle p-4">
                <summary>@t('Developer details') &mdash; {{ data_get($errorDebug, 'class') }}</summary>
                <pre>{{ data_get($errorDebug, 'message') }}</pre>
                <pre>{{ data_get($errorDebug, 'trace') }}</pre>
            </details>
        @endisset

        <a href="@routeUrl('store.home')">@t('Back to home')</a>
    </div>

    <script type="module">
        // Inline JS for the copy button. See pages/error.blade.php for the full version.
        for (const btn of document.querySelectorAll('[data-copy-target]')) { /* … */ }
    </script>
@endsection
```

---

## 3. Per-folder extension whitelist

| Folder            | Allowed extensions                          |
| ----------------- | ------------------------------------------- |
| `layouts/`        | `.blade.php`                                |
| `partials/`       | `.blade.php`                                |
| `components/`     | `.blade.php`                                |
| `pages/`          | `.blade.php`                                |
| `assets/css/`     | `.css`                                      |
| `assets/js/`      | `.js`                                       |
| `assets/images/`  | `.png .jpg .jpeg .webp .svg .gif`           |
| `assets/fonts/`   | `.woff .woff2 .ttf .otf`                    |
| `docs/`           | `.md`                                       |

Any other extension under these prefixes is ignored (the file is dropped from the stored theme, not rejected).

---

## 4. Forbidden Blade directives (hard reject)

These are blocked both at upload time and at runtime compile time:

- `@php` / `@endphp` — no inline PHP blocks
- `@inject` — no service container access
- `@eval` — no expression evaluation
- Dynamic targets in `@extends($x)`, `@include($x)`, `@includeIf($x)`, `@includeWhen($x)`, `@includeUnless($x)`, `@component($x)` — **only string literals are allowed**

```blade
{{-- BAD --}}
@php $price = $product->price * 1.2; @endphp
@include($partial)
@inject('formatter', App\Services\Formatter::class)

{{-- GOOD --}}
@include('components.price', ['amount' => data_get($product, 'price.price') ?? 0])
```

---

## 5. Forbidden raw PHP and smuggling

- No `<?php` or `<?=` tags anywhere in source
- No `` `backticks` `` (shell exec)
- No `$__env` access
- `@verbatim` blocks are scanned — you cannot hide a forbidden pattern inside one
- Blade comments `{{-- ... --}}` are stripped before scanning, so they cannot be used to bypass either

---

## 6. Forbidden functions (compiled-output scan)

The scanner tokenises the **compiled Blade output** and rejects calls to:

```
eval, exec, system, shell_exec, passthru, proc_open, popen,
assert, create_function,
file_get_contents, file_put_contents, fopen, unlink, chmod, mkdir,
include, require, include_once, require_once,
base64_decode, gzinflate, gzuncompress,
serialize, unserialize
```

Also rejected: `T_EVAL`, `T_INCLUDE`, `T_INCLUDE_ONCE`, `T_REQUIRE`, `T_REQUIRE_ONCE` construct tokens.

---

## 7. Forbidden helpers (raw-source scan)

These Laravel global helpers must never appear in theme source:

```
app(  request(  config(  env(  session(  cookie(  auth(
```

---

## 8. Forbidden facades (raw-source scan)

These facade static accessors are rejected:

```
Auth::  DB::  Schema::  Cache::  Storage::  Hash::
Route::  Mail::  Queue::  Event::  Log::
```

---
