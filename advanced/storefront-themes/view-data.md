---
title: View data
description: Global view data, the $store object, feature flags, pricing, variants, and rewards.
---

## 9.6 Config-driven view data — price visibility, add-to-cart gating, cart rewards

The platform injects a set of **config-driven flags** into every view (layouts, pages, partials, components) so a theme can react to the tenant's storefront settings without reading config itself (config helpers are forbidden — see §7). All of these mirror the Nexus SPA behaviour so the server-rendered storefront and the SPA stay in lockstep.

### The compliance contract

Every tenant capability flag documented in this section (the b2bware admin **Store Setup → Features** page: Customer Access, Checkout, Storefront features, Categories & SEO) drives real storefront behaviour. **Every theme — the bundled default theme and every uploaded theme — must respect every one of these flags exactly the way the default theme does.** It does not matter which flag it is: if the tenant switched a feature on or off, your theme's rendered output must reflect that.

This rule is **evergreen**: it covers every flag in the tables below today, and any tenant flag added to `$store` after this guide was last updated. If you find a boolean or enum key on `$store` that isn't documented yet, treat it the same way — gate whatever it controls, never render a dead link, and never invent behaviour a flag disagrees with.

**How to respect a flag — copy the default theme, don't invent your own logic.** The default theme (shipped alongside this guide) already implements every guard correctly. The *Feature-by-feature compliance guide* below names, per flag, the exact default-theme file(s) that implement it — open them and mirror the same `$store` check, in the same place, with the same fallback. Don't design a new gating pattern from the prose alone.

**Opting out is a conversation decision, not a theme-authoring one.** Skip a flag's guard **only** when the person you're building the theme for explicitly told you to skip that specific feature (e.g. "this theme doesn't need favorites" or "ignore coupons for this build"). If they said nothing about a flag, treat it as in scope and implement it exactly like the default theme — full stop. Never decide on your own that a flag is out of scope, and never invent a file, comment, or `README.md` section to declare an opt-out — there is no such mechanism. The only valid record of an intentional opt-out is the instruction the requester gave you.

Most of these flags also carry a **server-side safety net** (a 404, a rejected form submission, or price data that is empty/absent rather than merely hidden) — the table below marks which ones do and don't. Skipping the theme-side guard on a flag with a safety net breaks the UX (dead links, forms that only ever fail) rather than security; skipping one **without** a safety net changes what customers can actually do. Either way, respect every flag unless the requester explicitly told you to skip it — the safety net is a backstop, not a substitute for correct theme behaviour.

### Global flags (available in every blade)

| Variable          | Type    | Meaning                                                                                          |
| ----------------- | ------- | ------------------------------------------------------------------------------------------------ |
| `$me`             | object/null | The signed-in customer, or `null` for guests.                                                |
| `$isAuthenticated`| bool    | `true` when a customer is signed in.                                                             |
| `$canSeePrices`   | bool    | Whether prices may be shown to the current visitor.                                              |
| `$canAddToCart`   | bool    | Whether the current visitor may put items in the cart.                                           |
| `$cartLines`      | array   | Theme-ready cart line rows (image_url, name, sku, slug, unit_label, quantity, min/max_quantity, unit_price, original_price, has_discount, applied_catalog_rules, line_total, manage_stock, stock_quantity, stock_availability, delivery_date, **plus net/gross**: unit_price_excl/incl, original_price_excl/incl, line_total_excl/incl, tax_rate, has_tax). Consumed by `cart-line-items`; refreshes on AJAX. |
| `$freeDelivery`   | array/null | Nearest free-shipping threshold for the "X away from free delivery" banner (`remaining`, `target`, `current`, `met`, `is_currency`), or `null` when no such rule applies. Consumed by `cart-summary`. |
| `$store`          | array   | Store identity **and** capability flags (name, logo, support contacts, guest / registration / coupon / price rules) — read with `$store['key']`. Mirrors Shopify's `shop` object; see the keys table below. The **single** source for store info & flags. |
| `$passwordRequirements` | array | Human-readable, config-driven password requirement strings (e.g. `"At least 8 characters"`, `"One uppercase letter"`) that mirror the server-enforced rules. Render as a checklist on the register / reset-password forms (wrap each in `@t(...)`). May be empty; guard with `@if(count($passwordRequirements))` (lazy proxies are objects — do not use `empty()`). |
| `$passwordRules` | array | Structured variant of the same requirements for **live** client-side validation: each entry is `['rule' => 'min'|'uppercase'|'lowercase'|'number'|'special', 'label' => string, 'length' => int (min rule only)]`. Render each `<li>` with `data-password-rule="{{ $rule['rule'] }}"` (+ `data-min` for `min`) inside a `<ul data-password-checklist="<password-input-id>">`, then a small inline `<script type="module">` toggles `data-met` as the visitor types (see register / reset-password). Mirrors the server-enforced rules exactly. |
| `$isImpersonating` | bool | `true` when an admin agent is browsing on behalf of a customer (impersonation mode). Gate the `partials/impersonation-banner` partial on this variable — never use `request()` or `@php` to read a cookie. |
| `$companyRequiredFields` | array&lt;string,bool&gt; | Map of company field keys to required state, driven by the CustomerHub `company_required_fields` setting. Keys: `name`, `phone`, `vat_number`, `registration_number`, `website`, `address`. The `address` key covers the whole address block — `address_line_1`, `zip`, `city`, `country` are all required together when it is `true`. Falls back to `['name' => true, …rest false]` on read failure. Always injected, even on B2C tenants. Use `$companyRequiredFields['name'] ?? false` to add a required marker or `required` attribute. |
| `$messages` | array | **Post-form feedback** injected by the platform from the session bag after a redirect. Also called *flash messages*, *notices*, or *alerts* in other ecosystems — they're the same concept. Theme blades must never call `session()` directly (forbidden helper). Always four keys: `success`, `info`, `warning`, `error`. Each value is `string\|null`. **Always echo with `{{ }}`** — values may contain user-supplied input. Example: `@if($messages['success'] ?? null) <p>{{ $messages['success'] }}</p> @endif` |
| `$localeOptions` | array | Rich rows for the locale switcher — each `['code', 'label', 'short', 'flag', 'url', 'active']`. **Use this**, not raw `$availableLocales`, to render `partials/locale-switcher`. See §9.2. |
| `$availableLocales` | array | Low-level list of active locale tags (`string[]`). Prefer `$localeOptions` for UI. |
| `$defaultLocale` | string | Active locale tag (also mirrored as `$store['default_locale']`). |
| `$currency` | string | Active ISO-4217 currency (also `$store['default_currency']`). |
| `$searchQuery` | string | Current catalog search term (`q` query param), or empty string. |
| `$colorScheme` | string\|null | Active color scheme: `'light'`, `'dark'`, or `null` when unset. Emitted into `<html>` via `@storefrontColorScheme`. See §11.10. |
| `$currentPath` | string | Relative request URI — used as the redirect target for the color-scheme toggle. |
| `$hideChrome` | bool | `true` on standalone pages (e.g. the public proposal share page). Wrap header/footer/breadcrumbs in `@unless($hideChrome ?? false)` (see §2, §10). |
| `$cart`, `$cartItems`, `$cartCount`, `$cartTotals` | mixed | Cart summary snapshot injected on every page for the mini-cart / header count; the full cart page/sections receive the richer `$cartLines` + `$cartPricing`. |

**Tenant appearance CSS variables.** The platform also injects branding CSS the theme must not fight: `$tenantBrandCss` / `$tenantFontsHtml` (b2bware Appearance settings) and `$brandingCss` (per-customer category ramp). The default `shop.blade.php` prints them in a fixed **head cascade** — see §10 (Styling) for the exact order (`base.css` → tenant brand/fonts → theme `storefront.css` → branding). Do not reorder it.

The two gates are derived as (read them, don't recompute them):

```text
$canAddToCart = $isAuthenticated || allow_guest_checkout
$canSeePrices = $isAuthenticated || allow_guest_checkout || require_login_for_prices === false
```

> Because `$canAddToCart` implies `$canSeePrices`, any context where a visitor can add to cart (and therefore the cart/checkout pages) is always price-visible — you never need to re-gate prices inside the cart.

### `$store` keys

Like Shopify's `shop` object, `$store` carries both store **identity** and store-wide **capability flags**. All keys are always present (defaults baked in).

| Key                        | Type   | Default     | Meaning                                                            |
| -------------------------- | ------ | ----------- | ------------------------------------------------------------------ |
| `name`                     | string | app name    | Store name (from `store.name`, falls back to the platform name).   |
| `logo`                     | string\|null | `null` | Store logo URL, or `null` when unset.                              |
| `logo_dark`                | string\|null | `null` | Dark-scheme logo URL, or `null` (fall back to `logo`).             |
| `favicon`                  | string\|null | `null` | Favicon URL, or `null`.                                            |
| `product_placeholder`      | string\|null | `null` | Fallback product image URL used when a product has no media.       |
| `login_background_image`   | string\|null | `null` | Auth-layout background image URL (light), or `null`.               |
| `login_background_image_dark` | string\|null | `null` | Auth-layout background image URL (dark), or `null`.             |
| `login_background`         | string\|null | `null` | Scheme-resolved auth background (picks light/dark), or `null`.     |
| `contact_email`            | string\|null | `null` | Store contact email address, or `null`.                            |
| `contact_phone`            | string\|null | `null` | Store contact phone number, or `null`.                             |
| `contact_address`          | string\|null | `null` | Store postal/contact address, or `null`.                           |
| `legal`                    | array  | `[]`        | Legal link URLs keyed by type (e.g. `imprint`, `privacy`, `terms`); missing entries absent. |
| `social`                   | array  | `[]`        | Social profile URLs keyed by network (e.g. `facebook`, `instagram`, `linkedin`, `x`); missing entries absent. |
| `default_locale`           | string | active      | Active locale tag (BCP-47, e.g. `en-us`).                          |
| `default_currency`         | string | active      | Active ISO-4217 currency code.                                     |
| `home_page`                | string | `/products` | Normalised landing path.                                           |
| `allow_guest`              | bool   | `true`      | Guests may browse the storefront at all.                           |
| `allow_guest_checkout`     | bool   | `false`     | Guests may add to cart and check out without an account.           |
| `restrict_registration`    | bool   | `false`     | Self-service registration is disabled.                             |
| `company_required`         | bool   | `false`     | Registration must collect a company block.                         |
| `require_login_for_prices` | bool   | `false`     | Prices are hidden from guests until they sign in.                  |
| `zero_price_as_quote`      | bool   | `false`     | Zero/absent prices read "Request quote" instead of a 0 amount.     |
| `order_documents_enabled`  | bool   | `false`     | Customers may print/download their order documents from the order details page. |
| `coupons_enabled`          | bool   | `true`      | Coupon entry is offered on cart/checkout.                          |
| `delivery_date_enabled`    | bool   | `true`      | A preferred delivery date may be picked per cart line.             |
| `favorites_enabled`        | bool   | `true`      | The favorites / wishlist feature is offered on the storefront.     |
| `reorder_enabled`          | bool   | `true`      | Customers may re-order a completed order from their account.       |
| `catalog_export_enabled`   | bool   | `false`     | Opt-in module (`catalog_export.enabled`): renders the account "Catalog export" page/nav item and enables the tokenized public share link for a customer's stored export. |
| `quick_order_enabled`      | bool   | `false`     | Opt-in Quick Order (SKU autocomplete + CSV bulk add) account feature. |
| `variation_display_mode`   | string | `table`     | How a configurable product's variants are presented: `table` or `dropdown`. |
| `indexable`                | bool   | `true`      | Search engines may index the storefront; drives `<meta name="robots">` automatically. |
| `display_prices_with_tax`  | string | `excluding_tax` | How catalog/cart prices are shown: `excluding_tax` (net, B2B), `including_tax` (gross, B2C) or `both`. Follows the tenant's TaxHub setting. |

### Feature-by-feature compliance guide

One row per tenant-toggleable feature from the Features admin page (plus `quick_order_enabled`, wired the same way but not yet on that page's UI). **Server safety net** tells you whether the platform also blocks the underlying action server-side — skipping the theme guard on those still breaks the UX, just not security — or whether the theme is the *only* gate, in which case skipping it changes what a customer can actually do. **Respect it by** names the exact default-theme file(s) that already implement the guard correctly — open them and copy the pattern rather than inventing your own.

| Feature (Features admin page)          | `$store` key                                          | Default   | Server safety net                                                                                      | Respect it by |
| --------------------------------------- | ------------------------------------------------------ | --------- | -------------------------------------------------------------------------------------------------------- | -------------- |
| Require login to use storefront         | `allow_guest` (inverted)                                | `true`    | Full — guests are redirected to the login page before any blade renders.                                  | Nothing to do — never gate anything on this key yourself; the default theme has no file that checks it either. |
| Allow guest checkout                    | `allow_guest_checkout` → derived `$canAddToCart`        | `false`   | Full — checkout redirects guests to login; a guest cart-add POST is re-checked.                           | Gate every add-to-cart control/form on `$canAddToCart` — mirror `components/add-to-cart-button.blade.php`. |
| Require login to see prices             | `require_login_for_prices` → derived `$canSeePrices`    | `false`   | Full — price data itself is empty/absent server-side, not just hidden by CSS.                             | Gate every price render on `$canSeePrices` — mirror `components/price.blade.php`. |
| Require company details (register)      | `company_required` (+ `$companyRequiredFields`)         | `false`   | Full — the register submit rejects missing required fields server-side.                                   | Show the `company_*` register fields only when true — mirror `pages/register.blade.php` (see §9.5 *Reading registration config*). |
| Do not allow registration                | `restrict_registration`                                 | `false`   | Full — register routes 404 when restricted.                                                               | Hide every register link/nav item when true — mirror `partials/header.blade.php` and `pages/login.blade.php`. |
| Treat 0€ prices as request quote        | `zero_price_as_quote`                                   | `false`   | None — presentation only.                                                                                  | Re-use `components/price.blade.php`, which already implements this. |
| Allow printing order documents          | `order_documents_enabled`                               | `false`   | None — the control triggers a client-side print of the customer's own already-visible order page; there is no separate document endpoint to protect. | Only render the print control on the order page when true — mirror `pages/account/order.blade.php`. |
| Enable coupon code input                 | `coupons_enabled`                                       | `true`    | Full — a coupon-apply POST is rejected server-side when disabled.                                         | Only render the coupon form when true — mirror `partials/cart-discounts.blade.php` and `partials/checkout-summary.blade.php`. |
| Allow custom delivery date               | `delivery_date_enabled`                                 | `true`    | Full — the delivery-date POST is rejected server-side when disabled.                                      | Only render the delivery-date picker when true — mirror `partials/cart-line-items.blade.php`. |
| Enable favorites                         | `favorites_enabled`                                     | `true`    | Full — every favorites route 404s when disabled.                                                          | Hide every favorites entry point when false — mirror `components/product-card.blade.php`, `partials/header.blade.php`, `partials/footer.blade.php` and `partials/account-nav.blade.php`. |
| Enable reorder                           | `reorder_enabled`                                       | `true`    | Full — the reorder route 404s when disabled.                                                              | Only render Re-order on a completed order when true — mirror `pages/account/order.blade.php` and `pages/account/orders.blade.php` (see *Reorder entry-point pattern* below). |
| Enable catalog export                    | `catalog_export_enabled`                                | `false`   | Full — the export page and public feed both 404 when disabled.                                            | Only render the account nav item, export page and preview/fields partials when true — mirror `partials/account-nav.blade.php` and `pages/account/catalog-export.blade.php`. |
| Allow search engines to index            | `indexable`                                              | `true`    | Automatic — platform-rendered.                                                                             | Nothing to do — keep `@storefrontSeo` in every layout; never hardcode your own robots meta tag. |
| Product variation display mode           | `variation_display_mode` (`table` or `dropdown`)        | `'table'` | None — presentation only.                                                                                  | Branch your variant UI on this value — mirror `partials/product-details.blade.php` (see *Configurable products* below). |
| Quick Order & CSV upload _(same tenant_config family; not yet on the Features page)_ | `quick_order_enabled` | `false` | Full — every Quick Order route 404s when disabled. | Only render the account nav link and Quick Order page when true — mirror `partials/account-nav.blade.php` and `pages/account/quick-order.blade.php`. |

### One source per concept

Each kind of data has **exactly one** canonical access path — don't reach for an alternative that returns the same value:

| Need                                                                  | Use                                                   | Avoid                                                        |
| --------------------------------------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------ |
| Store info & capability flags (name, logo, coupons, registration, guest checkout, prices) | `$store['key']` (normalised, defaults baked in) | re-reading raw config — already resolved into `$store`       |
| Cart item count                                                       | `$cartCount`                                          | re-counting `$cartItems`                                     |
| Cart totals                                                           | `$cartTotals`                                         | re-summing line items                                        |

Everything a theme needs is delivered as **curated view data** — the global variables above plus the per-page data documented throughout this guide. There is no arbitrary settings reader; if a value is already injected, use the injected variable rather than reading it a second way.

### Optional curated view data (lazy)

Besides the always-on globals (`$me`, `$store`, `$cartCount`, …), themes may read a
**curated optional set** on any Blade. The platform binds each key as a lazy proxy:
the resolver runs **at most once per request**, and **only when the Blade touches
the variable**. Untouched keys cost nothing.

Do **not** use `@isset($recentOrders)` (the proxy is always “set”). Prefer:

- collections: `@forelse($recentOrders as …)` / `$recentOrders->isEmpty()`
- flags / counts / strings: `@if(count($canAccessAdmin))`, `@if(count($favoritesCount))` — **not** `empty()` (proxies are objects; PHP `empty()` is always false for objects)
- arrays: `$companyRequiredFields['name']`, `collect($favoriteIds)->contains($id)`

Never fetch customer orders or account PII through `@fetch` — use these keys.

| Variable | Type | Notes |
| --- | --- | --- |
| `$recentOrders` | Collection | Up to five newest non-draft orders (line items + shipping/billing). Empty for guests. Account index may pass 3 eagerly. |
| `$lastOrder` | order\|null | Newest non-draft order, or `null`. |
| `$loyaltyHome` | array | Loyalty dashboard payload; guest-safe defaults when LoyaltyHub is absent. |
| `$accountOverview` | array | `orders_count`, `open_orders`, `lifetime_spend`, `favorites_count`, `addresses_count`. |
| `$favoritesCount` | int | Badge-friendly count (use `count(...)`). |
| `$isAgent` | bool | Agent role or impersonation; use `count($isAgent)`. |
| `$rootCategories` | Collection | Navigable root categories with children. |
| `$favoriteIds` | array | Active list product ids; `[]` for guests. Prefer `collect($favoriteIds)->contains(...)`. |
| `$canAccessAdmin` / `$adminUrl` | bool / string\|null | Admin hand-off; use `count(...)`. |
| `$favoritesLists` | array | Lists + `active_list_id`; eager on the favorites page. |
| `$cartLines` | array | Theme-ready cart line rows (see cart-line-items). |
| `$freeDelivery` | array\|null | Free-shipping threshold banner payload. |
| `$cartProgress` | array | RuleHub reward progress; eager on the cart page. |
| `$passwordRequirements` / `$passwordRules` | array | Auth-form checklist data; eager on register. |
| `$companyRequiredFields` | array&lt;string,bool&gt; | Company field required map; eager on register. |
| `$catalogExportSummary` | array\|null | Safe export readiness fields (no raw token). |
| `$apiKeysCount` | int | API key count for badges. |

**Home page:** an uploaded theme may add `pages/home.blade.php` (`/{locale}/home`).
It receives the same globals + optional keys. Prefer `$me` / `$me->company` (including
trusted rich-text `conditions_2`) over page-only aliases. Order data is curated —
render `$recentOrders` and use the documented `reorder` form for completed orders.

### Hiding prices

Gate **every** price render on `$canSeePrices`, and offer a sign-in path when it's off. The bundled `components/price.blade.php` does this for you, so re-using that component is the simplest route:

```blade
@if($canSeePrices)
    <span class="price text-lg text-headings">{{ formatCurrency($amount) }}</span>
@else
    <a href="@routeUrl('store.login')" class="text-primary">@t('Log in to see prices')</a>
@endif
```

The platform binds these globals to **every** storefront view, so they're always present — read them directly, with no `?? default`.

### Net vs gross price display (VAT)

Whether prices read **net** (excl. VAT — the B2B default), **gross** (incl. VAT — B2C) or **both** follows the tenant's TaxHub setting, exposed as `$store['display_prices_with_tax']` (`excluding_tax` | `including_tax` | `both`).

**Themes never compute tax.** TaxHub is the single source of truth: the platform pre-splits every price into its net and gross parts in PHP (`StorefrontTaxDisplay`) and hands the theme a ready view-model. The bundled `components/price.blade.php` already renders all three modes from it, so re-using that component is all you need.

Pass the component a `priceView` view-model:

```blade
{{-- Catalog grid/list: look it up from the page's $priceViews map by product id --}}
@include('components.price', [
    'priceView' => data_get($priceViews ?? [], (string) $product->id),
    'amount'    => data_get($product, 'finalPrice.price') ?? data_get($product, 'price.price') ?? 0,
])
```

The view-model carries `current_excl`, `current_incl`, `compare_excl`, `compare_incl` and `has_tax`. Where it comes from:

| Context | Source |
| ------- | ------ |
| Catalog (products / category / favorites) | `$priceViews` — a `[product_id => view-model]` map; look up by id. |
| Product page | `$priceView` (the active variant) + `$crossSellPriceViews` (one per cross-sell card). |
| Cart lines | each `$cartLines` row already carries `unit_price_excl/incl`, `original_price_excl/incl`, `line_total_excl/incl`, `tax_rate`, `has_tax`. |

**Availability rule (important):** an "excl. VAT" / "incl. VAT" label is shown **only** when the item actually carries tax (`has_tax` — TaxHub resolved a non-zero rate). With no tax, net === gross and the price renders once, unqualified — never invent a VAT figure you don't have. A theme passing only `amount` (no `priceView`) gets exactly this single-figure behaviour, so existing price calls keep working unchanged.

### Per-customer pricing — prices are server-authoritative

**A theme never sets, computes, or fetches a price.** Every price — on the catalog grid, the product page, and each cart line — is computed on the server and handed to the theme as a ready value (`$priceViews` / `$priceView` / `$cartLines`). Render those; do not multiply, discount, or call an external pricing API from Blade.

When the tenant connects a pricing integration (for example an ERP such as **Mesonic** real-time pricing), the platform automatically fills these same view-models with the **signed-in customer's own price** — and that displayed price is exactly what the cart will charge. The catalog list price is shown struck-through next to it when it is higher. This needs **no theme changes**: a theme that simply renders `$priceViews` / `$priceView` shows personalised prices for free. (Older themes that fetched ERP prices client-side with `@fetch` should drop that and just render the supplied view-models — `@fetch` is for content, never pricing.)

### Gating add-to-cart

Only render the `cart-add` form when `$canAddToCart` is true; otherwise link to login. The bundled `components/add-to-cart-button.blade.php` already implements this:

```blade
@if($canAddToCart)
    @storefrontForm('cart-add', ['class' => 'add-to-cart'])
        <input type="hidden" name="product_id" value="{{ $product->id }}">
        <input type="hidden" name="quantity" value="1">
        <button type="submit">@t('Add to cart')</button>
    @endstorefrontForm
@else
    <a href="@routeUrl('store.login')" class="add-to-cart--login">@t('Log in to purchase')</a>
@endif
```

This is **UX only** — the server independently enforces the same rule: a guest POST to `store.cart.add.post` while `allow_guest_checkout` is off is redirected to login. You cannot bypass the gate by hand-crafting a request, and you don't need to re-implement that check.

### Configurable products (variants)

A **configurable** product has child **variants** (e.g. per Size / Colour). The platform treats variants as buy-options of their parent, never as standalone catalog entries:

- **Listings hide variants.** The products and category pages list root products only (the catalog applies `exclude_child_products`), so a configurable product appears once and its counts stay truthful.
- **A variant's own URL redirects to its parent with `?variant=<id>`.** Opening `/{locale}/products/<variant-slug-or-id>` 302-redirects to the parent product page **and keeps `?variant=<child id>`**, so table mode lands on the dedicated variant view (see below). Links stay canonical — variants are never standalone catalog pages.
- **Listing cards link to the product page, never add directly.** A listing card can't choose a specific variant, so a configurable product renders a **"Choose options"** link to its parent product page (where the variant picker / bulk-variant table lives) instead of an add-to-cart control. This applies to every catalog surface — grid and list cards, favorites and cross-sells — via `components/add-to-cart-button.blade.php` and the `product-card` list row, keyed off `data_get($product, 'product_type') === 'configurable'`. Simple products keep their normal add-to-cart (the list row keeps its quantity stepper). This mirrors Nexus and is the canonical pattern uploaded themes should follow.

How the parent product page presents its variants follows the tenant flag **`$store['variation_display_mode']`** (`'table'` default | `'dropdown'`). The default theme implements both; a custom theme can read the data below and build anything (a swatch grid, a matrix, …).

**Variant view-data** (present on the product page; empty for simple products):

| Variable | Shape |
| -------- | ----- |
| `$variants` | Collection of the public child products (live models). |
| `$selectedVariant` | **Dropdown:** the variant from `?variant=<id>`, else the first public child (drives price + add-to-cart). **Table:** only set when `?variant=<id>` is present (opens the variant view); otherwise `null` so the parent gallery / bulk table stay on the parent. |
| `$galleryImages` | `list<{ url, alt }>` for `components/product-gallery`. Own images only: `is_primary` image first, then remaining images by `sort_order`, de-duped by URL. **Table (no `?variant=`):** parent gallery. **Table variant view:** variant images (parent only if the variant has none). **Dropdown:** variant images first, then parent images appended (URL-de-duped). Render the thumbnail rail whenever `count($galleryImages) > 1`. |
| `$isVariantView` | `true` in **table** mode when `?variant=<id>` resolved to a child — single-buy UI for that variant, bulk table hidden, back-to-parent control shown. |
| `$displayProduct` | The model whose name / SKU / short description the theme should show: the selected variant when `$isVariantView`, otherwise the parent `$product`. |
| `$parentUrl` | Absolute path back to the parent product page (no `?variant=`). Non-null only when `$isVariantView`. |
| `$variantColumns` | Ordered list of parent-defined variation-axis attribute names (`ParentProductAttribute`) — the table columns. |
| `$variantRows` | One row per variant: `{ id, sku, name, image, attributes: [{ id, code, name, value, type, use_for_storefront_variant_filtering }], priceView, unit_amount, stock: {manage, available, quantity, low, min, max} }`. `priceView` feeds `components/price`; `image` is a raw URL (wrap in `@storefrontImage`) — the variant's own primary, else the parent's. In table mode, wrap the thumbnail in a link to `/{locale}/products/{{ $productSlug }}?variant={{ $row['id'] }}`. |
| `$variantFilters` | Typed filter controls for the variation table (see below). Empty when no axis is flagged or when display mode is not `table`. |

**Table-mode variant view.** When `$isVariantView` is true the default theme:

1. Renders `$displayProduct` title / SKU / short description and `$galleryImages` for that variant.
2. Shows the single-buy block (price, stock, add-to-cart) instead of the bulk variant table.
3. Shows a **"Choose options"** link to `$parentUrl` so the shopper can return to the parent (gallery + variant table).
4. Does **not** append parent images to the variant gallery (parent is only used when the variant has no images of its own).

**`$variantRows[*].attributes`** — each axis value on a row:

| Field | Meaning |
| ----- | ------- |
| `id` | Attribute id. |
| `code` | `attribute_code`. |
| `name` | Display name (matches an entry in `$variantColumns`). |
| `value` | Raw string value for this variant. |
| `type` | Supported variation-axis type: `select`, `radio`, `swatch`, or `boolean`. |
| `use_for_storefront_variant_filtering` | `true` when this axis should expose a filter control above the table. |

**`$variantFilters`** — opt-in per attribute. An entry appears only when:

1. `$store['variation_display_mode'] === 'table'`, and
2. the attribute is a variation axis on this product, and
3. the attribute has `use_for_storefront_variant_filtering=true` in AttributesHub, and
4. there are enough distinct values for the control to be useful (e.g. more than one option for `options`/`boolean`).

Shape of each entry:

| Field | Meaning |
| ----- | ------- |
| `name` | Attribute display name (matches `$variantColumns`). |
| `code` | `attribute_code`. |
| `type` | Attribute type. |
| `mode` | Theme control mode: `options` or `boolean`. |
| `values` | Distinct sorted labels used by the filter control. |

Mode mapping from attribute type:

| Type | Mode |
| ---- | ---- |
| `select` / `radio` / `swatch` | `options` |
| `boolean` | `boolean` |

Only `select`, `radio`, `swatch`, and `boolean` attributes are supported as variation axes. Other attribute types never appear in `$variantFilters`.
Boolean row values and filter option values are normalized to the strings `true` / `false`; themes should translate their visible labels to `Yes` / `No`.

Custom themes can rebuild the filter UI from this contract without depending on the default partial's markup:

```blade
@if(($store['variation_display_mode'] ?? 'table') === 'table' && !empty($variantFilters))
    <div class="product__variant-filters">
        @foreach($variantFilters as $i => $filter)
            <label>
                <span>{{ $filter['name'] }}</span>
                <select data-variant-filter data-filter-index="{{ $i }}" data-filter-mode="{{ $filter['mode'] ?? 'options' }}">
                    <option value="">@t('All')</option>
                    @foreach(($filter['values'] ?? []) as $value)
                        <option value="{{ $value }}">{{ data_get($filter, 'mode') === 'boolean' ? ($value === 'true' ? t('Yes') : t('No')) : $value }}</option>
                    @endforeach
                </select>
            </label>
        @endforeach
    </div>
@endif

{{-- Row values for client-side matching: --}}
@foreach($variantRows as $row)
    <tr data-variant-row
        @foreach($variantFilters as $i => $filter)
            data-filter-{{ $i }}="{{ data_get(collect($row['attributes'])->firstWhere('name', $filter['name']), 'value', '') }}"
        @endforeach
    >
        {{-- … --}}
    </tr>
@endforeach
```

Matching is an exact string comparison for both `options` and `boolean`. Toggle row visibility with `row.style.display` (not the `hidden` attribute) so mobile `max-md:block` cards stay correct.

**Dropdown mode — server re-render.** When `variation_display_mode === 'dropdown'`, the default theme renders one `<select>` per varying axis. Choosing a full, available combination resolves to a variant id and **re-renders the whole product detail server-side** for that variant via the **`product-details` section** (§9.7): the picker calls `Storefront.selectVariant(productId, variantId)`, which re-fetches the section with `?product&variant`, swaps it with a short loading fade, sets `?variant=<id>` in the URL (shareable / refresh-safe) and emits `storefront:variant:selected`. Because the server re-renders, price, stock, tier prices and add-to-cart stay tax- and rule-correct — the browser never recomputes money. A variant's own `?variant=<id>` URL is always a valid deep link; the picker itself is a JS enhancement (with JS off, deep-link via those URLs or use table mode).

**Bulk add (`cart-bulk-add`).** The table posts a quantity per variant in one request as an `items[<product_id>]` map; the server adds every positive line with **partial success** — valid lines go in, unpurchasable / out-of-stock ones are skipped and named in the flash/toast. It is AJAX-enhanced like the other cart forms and fires `storefront:cart:added` with one `added` entry per variant, so the add-to-cart confirmation (§9.7) lists them all. Gate it on `$canSeePrices && $canAddToCart`.

```blade
@storefrontForm('cart-bulk-add')
    @foreach($variantRows as $row)
        <input type="number" name="items[{{ $row['id'] }}]" value="0" min="0" data-variant-qty>
        @include('components.price', ['priceView' => $row['priceView'], 'amount' => $row['unit_amount'] ?? 0])
    @endforeach
    <button type="submit">@t('Add everything to cart')</button>
@endstorefrontForm
```

Live row/total maths and the attribute filters are pure client-side enhancement (an inline `<script type="module">`): read each rendered price's `data-amount` for the unit, sum on `input`, and toggle each row's inline `display` on filter `change`/`input`. With JS off the form still posts and the cart updates the classic way.

**Responsive (mobile cards).** Below `md` (768px) the bulk table reflows from a row-based table into one **card per variant**, so phones and portrait tablets never scroll sideways. The `<table>` / `<thead>` / `<tbody>` / `<tr>` / `<td>` carry `max-md:` display overrides (`max-md:block`, `max-md:hidden`, `max-md:flex`); each data cell gains a `md:hidden` label span (reusing the column / `SKU` / `Price` / `Quantity` strings — no new keys) and the thumbnail centres on top of the card. The desktop table markup/classes are unchanged. Two gotchas: (1) the filter script toggles **`row.style.display`** (an inline style), never the `hidden` attribute, because an inline style is the only thing that reliably outranks `max-md:block`; (2) `max-*` variants are not precompiled, so the `max-md:` utilities are force-included in `resources/css/storefront.css` (`@source inline(...)`) and `base.css` is rebuilt (see §10.3). No custom CSS is involved.

### Cart reward progress bars

The cart page receives **`$cartProgress`** — progress toward each eligible cart price-rule's threshold, sourced from RuleHub. Render a bar per rule so shoppers see how close they are to the next discount / free-shipping reward (mirrors the Nexus cart rewards row).

`$cartProgress` is a list; each entry is shaped:

| Field               | Meaning                                                                                  |
| ------------------- | ---------------------------------------------------------------------------------------- |
| `rule_name`         | Human label for the rule.                                                                 |
| `action_type`       | `by_percent`, `by_fixed`, `to_fixed`, `per_item_fixed`, `tiered`, …                       |
| `action_amount`     | Reward magnitude (percent or currency amount, per `action_type`).                         |
| `free_shipping`     | `no` / `matching_items` / `whole_shipment` — non-`no` means a free-shipping reward.       |
| `met`               | `true` when the reward is already unlocked.                                               |
| `blocked`           | `true` when the rule can't currently apply (wrong customer group, usage limit, coupon required) — **skip these**. |
| `show_progress_bar` | Per-rule visibility toggle from the admin — **skip when `false`**.                         |
| `thresholds`        | List of thresholds (see below); usually one.                                              |

Each threshold:

| Field           | Meaning                                                                        |
| --------------- | ------------------------------------------------------------------------------ |
| `attribute`     | Cart attribute tracked — `subtotal_price` / `total_price` / `price` are money.  |
| `current_value` | Current cart value for that attribute.                                          |
| `target_value`  | Value needed to unlock the reward.                                              |
| `remaining`     | `target_value − current_value` (clamped at 0).                                  |
| `percentage`    | Pre-computed 0–100 progress.                                                    |
| `met`           | `true` when this threshold is reached.                                          |

Rendering rules:

- **Visibility is per rule** — each rule carries its own `show_progress_bar`. There is **no** tenant-wide "show cart progress" switch; skip a rule when `blocked` is true or `show_progress_bar` is false, and render nothing when `$cartProgress` is empty.
- Format `current_value` / `target_value` / `remaining` with `formatCurrency(...)` when `attribute` is a money field (`subtotal_price`, `total_price`, `price`), otherwise `formatNumber(...)`.
- `t()` has **no interpolation** (§9.1) — build dynamic phrases from translatable fragments (`@t('Add') {value} @t('to unlock')`), never `t('Add :amount …', [...])`.

The bundled `default` theme ships this as `partials/cart-rewards.blade.php`, included from `pages/cart.blade.php`:

```blade
@foreach($cartProgress as $reward)
    @continue(($reward['blocked'] ?? false) || ($reward['show_progress_bar'] ?? true) === false || empty($reward['thresholds']))
    @foreach($reward['thresholds'] as $threshold)
        <div class="cart__reward">
            <div class="cart__reward-track h-2 w-full rounded-full bg-surface overflow-hidden">
                <div class="cart__reward-fill h-full rounded-full {{ ($reward['met'] ?? false) ? 'bg-success' : 'bg-primary' }} transition-all duration-300"
                     style="width: {{ max(0, min(100, (float) ($threshold['percentage'] ?? 0))) }}%"></div>
            </div>
        </div>
    @endforeach
@endforeach
```

> **Custom themes:** `cart-rewards.blade.php` is now a **canonical partial** (§2), rendered as the `cart-rewards` AJAX section (§9.7). Override it to restyle the reward bars — the `$cartProgress` view data is unchanged. (You may still render `$cartProgress` inline in your own `pages/cart.blade.php` if you prefer not to use the section.)

---
