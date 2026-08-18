---
title: Analytics & slots
description: Consent-gated analytics and @storefrontSlot module/CMS content slots.
---

## 9.13 Analytics, cookie consent & custom scripts

The platform ships a **complete, consent-gated analytics layer** — Google Tag Manager, Google Analytics 4 and Microsoft Clarity — that a store owner turns on in the B2BWare admin (**Store setup → Integrations**). A theme opts in with **two drop-once directives**; everything else (which tag loads, the cookie-consent modal, the e-commerce events) is handled by the platform. There is **nothing tenant-specific to hard-code** in a theme, and nothing loads for a store that has not configured tracking.

### The directive

Add `@storefrontAnalytics` once, as high as possible inside `<head>`, to every layout (`layouts/shop.blade.php`, `layouts/auth.blade.php` and any custom layout). It emits the `window.dataLayer` init, a small config object, and the **on-demand** analytics runtime (loaded only when tracking is configured):

```blade
<head>
    @storefrontColorScheme
    @storefrontAnalytics   {{-- keep this as high as possible in <head> --}}
    ...
</head>
```

It is a **safe no-op** when the store has configured no tracking — it emits nothing, loads no script and sets no cookie — so include it always.

### How it works (you wire none of this)

- **Nothing loads before consent.** On the first visit the runtime shows a first-party cookie-consent modal (Accept / Reject). No Google or Clarity tag — and no request to them — happens until the visitor **accepts**. A rejection is remembered and nothing loads. The decision is stored in `localStorage`, scoped to the store.
- **One method — the store's explicit choice.** The store owner picks a single method in the admin — Google Tag Manager (recommended) or GA4 — and the storefront loads **only** that one; the other tag never loads, even if a stale id is still saved (Google recommends against running both). Either way the same e-commerce `dataLayer` events fire, so your theme does nothing differently.
- **Microsoft Clarity** loads the same consent-gated way. A pasted Clarity script wins over a project id.

### E-commerce events (automatic)

The platform pushes standard [GA4 e-commerce](https://developers.google.com/analytics/devguides/collection/ga4/ecommerce?client_type=gtm) events to the `dataLayer` for you — a theme assembles **none** of them, so any GTM / GA4 tag or Google Ads conversion works out of the box.

- **Browsing events** fire automatically as the visitor moves through the store: `view_item_list` (catalog + category listings), `view_item` (product page), `view_cart` (cart page) and `begin_checkout` (checkout page). Each carries the relevant products as GA4 `items`.
- **Interaction events** fire as the visitor acts: `add_to_cart` and `remove_from_cart` ride the cart AJAX runtime, so the default add / remove forms need no extra markup; `select_item` fires when a product in a list is clicked (see the opt-in hook below).
- **`purchase`** — the conversion Google Ads needs. It is pushed **exactly once** on the order-confirmation page after checkout (works for logged-in customers and guests, and survives the payment-provider round-trip). It **never re-fires** on refresh or when the order is viewed again later, so revenue is never double-counted. It carries the order id, value, tax, shipping, currency and line items.
- **Item fields.** Every product in an event's `items` array carries `item_id` (SKU, falling back to the id), `item_name`, `price` and `quantity`, plus — when the data exists — `item_category` (the product's primary category), `item_variant` (a configurable product's chosen options, e.g. `Red / XL`) and `item_brand`. **Brand** is read from a product attribute: the store owner names it in the admin (the `item_brand_attribute` setting), and the platform otherwise falls back to an attribute whose code is `brand` or `manufacturer`. You wire none of this — the platform fills the fields from the catalog.
- **Clean events.** The platform clears the previous `ecommerce` object (`dataLayer.push({ ecommerce: null })`) before every event, per Google's guidance, so values never leak between events. If you inspect the `dataLayer` in the console you will also see GTM's own `gtm.uniqueEventId` on each entry — that is GTM's internal bookkeeping, **not** something the storefront pushes; don't add it yourself.

No personal data is ever put in the `dataLayer`, and prices honour the same visibility rules as the rest of the storefront.

### Opting a product card into `select_item`

`select_item` fires when a visitor clicks a product link inside an element carrying the `data-analytics-item-*` attributes. The default theme's `product-card` already includes them; if you author your own card markup, add them to its root element so clicks are tracked:

```blade
<article
    data-analytics-item-id="{{ ($product->sku ?? '') ?: ($product->id ?? '') }}"
    data-analytics-item-name="{{ $product->name ?? '' }}"
    data-analytics-item-category="{{ data_get($product, 'categories.0.category.name') ?? data_get($product, 'category.name') ?? '' }}"
    @if($canSeePrices) data-analytics-item-price="{{ data_get($product, 'finalPrice.price') ?? data_get($product, 'specialPrice.price') ?? data_get($product, 'price.price') ?? '' }}"@endif
>
    <a href="@routeUrl('store.product', ['identifier' => $product->id])">…</a>
</article>
```

Only `data-analytics-item-id` (or `data-analytics-item-name`) is required; `data-analytics-item-category` is optional and enriches the click, and the price is omitted when prices are hidden. `select_item` carries the id, name, category and price — the higher-signal server events (`view_item`, `add_to_cart`, `view_cart`, `purchase`) additionally carry brand and variant. `add_to_cart` / `remove_from_cart` need no such hook — they ride the platform cart forms.

### Custom events & GTM tracking

The platform pushes the e-commerce funnel above; **everything else is tracked in Google Tag Manager**, not in theme code. GTM's own triggers (clicks, form submissions, element visibility, …) capture any interaction — as long as they can target the element.

> **Rule — every action needs an `id`.** A custom theme MUST give every actionable element a stable, unique, descriptive `id`: buttons, links (`<a>`), `<form>`s and their submit controls, and anything a marketer might want to measure (a "Request demo" button, a newsletter form, a `tel:` / `mailto:` link). Without an `id`, GTM can't reliably target the action and it can't be measured. Example: `id="request-demo"`, `id="newsletter-form"`, `id="header-phone-link"`.

If a theme really needs to emit its own event (e.g. `generate_lead` after a successful AJAX submit), push straight to the data layer — the platform adds nothing on top:

```blade
<script type="module">
    // window.dataLayer exists once @storefrontAnalytics has run (analytics enabled).
    window.dataLayer?.push({ event: 'generate_lead', form_name: 'Demo Request' });
</script>
```

The theme owns whatever it pushes.

### Styling the consent modal (optional)

The modal renders with sensible defaults, so you can ship a theme without touching it. To restyle it, target these semantic classes in your `assets/css/storefront.css`:

- `.storefront-consent` — the full-screen overlay
- `.storefront-consent__panel` — the dialog card
- `.storefront-consent__title` · `.storefront-consent__description`
- `.storefront-consent__actions` · `.storefront-consent__accept` · `.storefront-consent__reject`

### A "Manage cookies" control (optional)

To let visitors reopen the consent choice (e.g. a footer link), add `data-storefront-consent-open` to any button or link — the runtime opens the modal on click and degrades to nothing with JS off:

```blade
<button type="button" data-storefront-consent-open>@t('Cookie settings')</button>
```

`window.StorefrontConsent` is also exposed (`.open()`, `.accept()`, `.reject()`, `.status()`) for use from your own inline module.

> **Consent is the store owner's legal responsibility.** The platform provides the gate; the store owner must ensure their GTM / GA4 / Ads setup complies with the rules for their market (e.g. GDPR, Google Consent Mode).

---

## 9.16 Slots (`@storefrontSlot`)

A **slot** is a named region the core theme exposes via `@storefrontSlot('key')`. It has two independent fills, rendered together:

1. **Module contributions** — shipped by **optional platform modules** rather than the core storefront (for example, a module that maps a customer-specific SKU to each product). The theme doesn't hard-code any module; each installed module fills the slots it cares about.
2. **Owner-authored content** — CMS content a shop manager assigns to the slot key in the admin block builder, resolved for the current tenant + locale.

You don't create or wire slots; the core theme already places them. With no module installed and no content assigned, a slot renders **nothing**, so it can sit in the markup unconditionally.

### What you get for free

The bundled default theme already places every slot, so a fresh theme (or one that extends the default partials) inherits all module contributions automatically — you do nothing. A module renders its own markup (its own blade, shipped inside the module), styled to sit naturally next to the surrounding content.

### Available slots

| Slot | Where it renders | Variables in scope |
| --- | --- | --- |
| `product.card.meta` | Product card, under the SKU (catalog / category listing) | `$product`, `$store`, `$locale`, … |
| `product.detail.meta` | Product detail page, under the SKU | `$product`, `$store`, `$locale`, … |
| `cart.line.meta` | Cart line item, under the SKU | `$line` (the cart line array), `$store`, … |
| `order.line.meta` | Account order detail, in the SKU cell | `$item` (the order line model), `$store`, … |

A module receives the surrounding surface's variables plus whatever it computes itself, so its override blade can read e.g. `$product` or `$line` directly.

### Owner-authored content slots

Besides module contributions, a slot also renders any CMS content a shop manager has assigned to its key in the admin block builder (for the current tenant + locale). Slots are discovered automatically by scanning `@storefrontSlot('key')` across the theme's blades — that scan is the source of truth, so `theme.json`'s `"slots"` map is informational only. The bundled theme gives **every** editable page a consistent pair of owner regions plus a few page-specific zones, which powers the admin "Theme Pages" area:

- `content-top` / `content-bottom` — the standard top-of-content and bottom-of-content regions on **every** editable page: catalog (`products`, `product`, `categories`, `category`), `cart`, `checkout`, `favorites`, all account pages (`account/index`, `account/profile`, `account/orders`, `account/order`, `account/shipping-addresses`, `account/billing-addresses`, `account/quick-order`, `account/catalog-export`), `__custom-page`, `proposal-preview`, `guest-order`, `customer-selection`, and the auth pages (`login`, `register`, `forgot-password`, `reset-password`, `verify-email`, `logout` — top only).
- `hero` — a **full-width** banner rendered **above the breadcrumbs** (via the layout's `@yield('hero')`, filled per page by `@section('hero')`) on the catalog pages `products`, `categories`, `category`, `product`.
- `announcement`, `footer-note`, `footer.promo` — site-wide (the `global` page): the top announcement bar and footer zones, declared in the shared layout / footer.
- `catalog.sidebar` (products, above the filter card) and `cart.promo` (cart) — page-specific extras. A page-specific slot must sit at a position `content-top` / `content-bottom` do not already occupy, otherwise the editor shows two indistinguishable regions.

> The self-contained error pages (`not-found`, `error`) carry **no** slots on purpose — they must never touch the database.

These promo/banner zones are self-serve: a manager schedules (start/end) and targets (all / customer group) each widget in the builder, and images below the fold lazy-load. An unassigned, expired or off-audience zone renders nothing, so it can be placed unconditionally.

Declare a content slot by simply placing `@storefrontSlot('key')` in the blade — the scanner discovers it, no `theme.json` edit required. A slot in the shared **layout** is a `global` (site-wide) slot; a slot in a **page** blade is scoped to that page, and the same key (e.g. `content-top`) can be reused across pages because each page resolves its own content. It renders nothing until content is assigned.

### Declaring slot context (builder data binding)

When a slot sits inside a loop or a record surface (a product card, a product detail page), the Theme Editor needs to know which Blade variables the slot exposes so an author can bind widgets to them ("From slot context"). Declare that with an optional **config object** as the second argument:

```blade
@storefrontSlot('product.card.meta', [
    'context' => [
        'product' => 'product',
    ],
])
```

- The outer argument is a PHP assoc array (the Blade equivalent of a JS object). **v1 only recognises `context`**; unknown top-level keys are ignored so future options can land without breaking themes.
- Inside `context`, key = the Blade variable already in scope (`$product`), value = the field-catalog schema key (`product`, `category`, `order`, `store`, `me`, `cart`). Shorthand `'product'` (list form) means schema = variable name.
- Runtime rendering is unchanged — surrounding view data is still captured via `get_defined_vars()`. The config is metadata for the Theme Editor only.
- An undeclared slot simply offers no slot context in the picker (page-level context like `me` / `cart` / `store` still applies).

The default theme declares product context on `product.card.meta` and `product.detail.meta`.

### Restyling a module's contribution (optional)

If you want a module's output to look different, override its blade — without touching the module — by shipping:

```
modules/<module-slug>/<view>.blade.php
```

Your file replaces the module's default blade for that slot. It receives the same variables the module passes to its blade (the surrounding scope **plus** the module's own values, e.g. a customer SKU string). To discover the exact `<module-slug>`, `<view>` name and the variables a specific module exposes, consult that module's documentation — the platform's slot list above only defines *where* a slot renders, not *what* each module puts in it.

The same authoring rules apply to these override files as to any other theme blade: the forbidden directives/functions/facades (§4–§8) are enforced, and both path segments must be lowercase and dash-separated (one nested level, `modules/<slug>/<view>.blade.php`).

---
