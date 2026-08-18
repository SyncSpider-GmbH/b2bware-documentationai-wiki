---
title: AJAX & runtime
description: AJAX sections, JavaScript events, window.Storefront, and loading states.
---

<Info>
This page also ships inside the default theme download under `docs/05-ajax-runtime.md`, so offline and AI-assisted authors have the same contract locally. This online version is always the latest.
</Info>

## 9.7 Sections, AJAX & progressive enhancement

The storefront is server-rendered, but cart actions — add to cart, change quantity, remove a line, apply / remove a coupon, clear the cart — update the page **in place, without a full reload**, the way Shopify does. This rests on two platform primitives a theme opts into purely through markup:

1. **Sections** — `@storefrontSection('id')` wraps a reusable render unit in a `[data-storefront-section="id"]` marker.
2. **The runtime** — `@storefrontScripts` loads a small, dependency-free platform script that intercepts cart forms, posts them with `fetch`, and swaps the affected sections.

Everything degrades gracefully: with JavaScript off (or the script absent) every form still submits the classic POST → redirect way. **Never rely on the AJAX path for correctness** — it is an enhancement layered on top of working HTML.

### How it works (the Shopify model)

A cart form POST is content-negotiated by the platform:

- A **normal** submit → `302` redirect (POST → redirect → GET), the page reloads. This is the no-JS fallback.
- An **AJAX** submit (the runtime adds `X-Requested-With` + `Accept: application/json`) → a JSON envelope bundling the new cart state **and** freshly rendered HTML for the sections currently on the page. The runtime swaps each section's `innerHTML`.

This mirrors Shopify's Cart Ajax API with bundled section rendering: one request both mutates the cart and returns the HTML to refresh.

### `@storefrontScripts` — required for AJAX

Add it **once**, just before `</body>`, in every layout (the bundled layouts already do this):

```blade
    @storefrontScripts
    @stack('scripts')
</body>
```

It emits a small config object (`window.__STOREFRONT__`) and the runtime, loaded as a native ES module (`<script type="module">` — module-scoped and deferred/non-blocking by default). Omit it and the storefront still works — the forms simply do full-page submits.

### Registered section ids

`@storefrontSection('id')` renders the platform-registered partial for `id`, wrapped in the swap marker. The id → partial map is **platform-owned** (a theme cannot register new ids), but every target partial is a canonical file you may override to restyle it:

| Section id         | Renders                               | Refreshes                                       |
| ------------------ | ------------------------------------- | ----------------------------------------------- |
| `mini-cart`        | `partials/mini-cart.blade.php`        | every cart mutation (header badge + summary)    |
| `cart-line-items`  | `partials/cart-line-items.blade.php`  | cart page — line rows + empty state             |
| `cart-discounts`   | `partials/cart-discounts.blade.php`   | cart page — coupon + applied rules              |
| `cart-summary`     | `partials/cart-summary.blade.php`     | cart page — totals                              |
| `cart-rewards`     | `partials/cart-rewards.blade.php`     | cart page — reward progress bars                |
| `checkout-summary` | `partials/checkout-summary.blade.php` | checkout page — coupon + totals                 |
| `product-details`  | `partials/product-details.blade.php`  | product page — the whole product detail, re-rendered for a chosen variant (see *Configurable products*) |
| `catalog-export-preview` | `partials/catalog-export-preview.blade.php` | account catalog-export page — live preview table of the first rows the current column/filter selection would export (refreshed as the form changes) |

The runtime refreshes **exactly the sections present on the current page** (plus `mini-cart`). On a product page only `mini-cart` exists, so add-to-cart just updates the header; on the cart page all cart sections refresh. No per-form wiring.

> A section partial must be **self-contained** — it owns its empty/non-empty branches (e.g. `cart-line-items` shows the empty-cart message when the count is 0), because the runtime swaps only that fragment. Read the global composer variables (`$cartItems`, `$cartLines`, `$cartCount`, `$store`, `$locale`) plus the section-specific extras the platform supplies: `$cartPricing` for `cart-summary` / `cart-discounts` / `checkout-summary` (plus `$freeDelivery` for `cart-summary`), `$cartProgress` for `cart-rewards`, `$preview` for `catalog-export-preview` (null when the module is off or the visitor isn't a signed-in customer — the partial then renders nothing, so the public sections route can never leak catalog rows).

> **A section may carry its own inline script.** `innerHTML` never runs `<script>` tags, so after a swap the runtime **re-executes** every `<script>` inside the swapped section — a section that ships an inline `<script type="module">` (e.g. `product-details` with its variant picker, tabs and bulk-table maths) re-arms itself every time it re-renders. Keep such scripts **element-scoped** (bind listeners to nodes *inside* the section, never `document`-level) so re-running them can't stack duplicate handlers.

> **Checkout sidebar layout.** The default theme renders `checkout-summary` *card-less* (no border/background of its own) inside the sidebar card on `pages/checkout.blade.php`, so the order totals visually merge with the terms checkbox + "Place order" button below them. Those controls — the `accept_terms` checkbox (wired to the tenant's `$store['legal']` Terms/Privacy URLs) and the submit button — live **outside** `@storefrontSection('checkout-summary')` but still **inside** the checkout `<form>`, so an AJAX coupon apply/remove swaps only the totals and never destroys the place-order button. Keep that ordering if you restyle the sidebar.

> **Custom checkout order-attributes.** The platform passes `$checkoutAttributes` to the checkout page — the tenant-defined order attributes (AttributesHub group `type=order`, `use_in_checkout=true`) with their option `values` eager-loaded. The default theme renders them as an "Additional details" panel of inputs **inside** the checkout `<form>`. Each attribute submits two fields: a hidden `attributes[<i>][attribute_id]` and a value field `attributes[<i>][value]` (an array `attributes[<i>][value][]` for `multiselect`). For `select`/`radio`/`swatch`/`multiselect` the submitted value is the option's raw `value` (the backend resolves it by that string). Map the input by `$attribute->type` (`text`, `textarea`/`richtext` → textarea, `number`, `date`, `datetime`, `boolean` → checkbox, `select`/`swatch` → dropdown, `radio`, `multiselect`); honour `$attribute->required`; surface errors with `@storefrontError('attributes.<i>.value')`. `media` attributes are **skipped** (a file upload isn't supported in this server-rendered flow) — don't configure a required `media` order-attribute for checkout.

> **Checkout addresses are company-aware.** `$billingAddresses` and `$shippingAddresses` on the checkout page are **not** the customer's own addresses alone — B2Bware is B2B-first, so each collection lists the customer's personal addresses first, followed by their **company** addresses (`$address->type === 'company'`, shared and managed by the company). This is what lets a customer who has no addresses of their own check out against the company's. Pre-selection follows the customer's own default, then the company default, then the first entry — `$defaultBillingAddressId` / `$defaultShippingAddressId` carry that id, and the same ids are seeded onto the cart so tax and shipping price against the visible selection. Both a personal and a company address can be *stored* with `default = true`, so the platform collapses `$address->default` to the single pre-selected entry before handing the collections to the theme — `@checked(old('billing_address_id', $defaultBillingAddressId) == $address->id)` and `@checked($address->default)` therefore agree, and only ever check one radio. Company addresses are **read-only** for the customer: don't offer "set as default", edit or delete actions on them (`data_get($address, 'type') === 'company'`), and label them so the shopper can tell them apart. On submit the server validates the posted id against the same address book: an address that is neither the customer's nor their company's is rejected.

### Auto-enhanced forms

Forms emitted by `@storefrontForm` for these types are enhanced automatically — no extra attributes needed:

`cart-add`, `cart-bulk-add`, `cart-update`, `cart-line-delivery-date`, `cart-remove`, `cart-clear`, `cart-coupon-apply`, `cart-coupon-remove`.

The platform stamps each with `data-storefront-form="<type>"` and the runtime finds them. To force one form to submit the classic (full-reload) way, add `data-storefront-ajax="off"`:

```blade
@storefrontForm('cart-clear', ['data-storefront-ajax' => 'off'])
```

A `name="quantity"` input inside a `cart-update` form — and a `name="delivery_date"` input inside a `cart-line-delivery-date` form — auto-submits on change (debounced); the **Update** / **Save** button is the no-JS fallback. The `quantity-selector` component's `−` / `+` buttons (`[data-action="inc"|"dec"]`) step the sibling quantity input and trigger the same debounced submit. Tag any control that exists only as a no-JS fallback with `data-storefront-no-js` so the runtime hides it once enhancement is active.

### Markup hooks

| Attribute                       | Effect                                                                                            |
| ------------------------------- | ------------------------------------------------------------------------------------------------- |
| `data-storefront-section="id"`  | Swap target — its `innerHTML` is replaced with the section's fresh HTML. Emitted by `@storefrontSection`. |
| `data-storefront-form="type"`   | Marks a cart form for enhancement. Emitted by `@storefrontForm` — don't set it yourself.          |
| `data-storefront-ajax="off"`    | Opt a single form out of enhancement (classic submit).                                            |
| `data-storefront-loading="off"` | Opt a single form out of the automatic loading state — no spinner, no progress bar. The form still submits (§9.9). |
| `data-storefront-loading-link`  | Put on a navigating `<a>` (e.g. "Proceed to checkout") to show the loading state — a spinner on the link + the top progress bar — the moment it's clicked, while the next page loads. Ignored for modified clicks (new tab/window), `target` / `download` links and non-navigating hrefs (§9.9). |
| `data-storefront-cart-count`    | Element text is set to the live item count after each mutation (badges outside the mini-cart).    |
| `data-storefront-cart-filled`   | Hidden when the cart is empty, shown when it has items.                                            |
| `data-storefront-cart-empty`    | Shown only when the cart is empty.                                                                 |
| `data-storefront-no-js`         | Hidden once the runtime is active (and re-hidden after section swaps) — use for explicit submit buttons that exist only as a no-JS fallback next to an auto-submitting control. |
| `data-storefront-modal-open="id"` | On click, opens the native `<dialog id="id">` via `showModal()`. Put it on a `<button type="button">` so it never submits a surrounding form. |
| `data-modal-close`              | On click, closes the nearest ancestor `<dialog>`. A click on the dialog backdrop also closes it; Escape is native to `<dialog>`. |
| `.storefront-busy`              | Applied by the runtime to the pressed submit control while a request is in flight — spinner + hidden label (§9.9). Restyle in theme CSS. |
| `[data-storefront-progress]`    | The top loading bar the runtime creates during a full-page submit (§9.9). Restyle in theme CSS. |

### Modals

There is **no** modal component to include &mdash; write a native `<dialog>` directly. The runtime wires opening/closing purely from markup (see the two attributes above), so there is **no** JS to write either. Trigger with `data-storefront-modal-open="<dialog-id>"` and close with `data-modal-close`, a backdrop click, or Escape.

> **Centering — required in every theme.** A `showModal()` dialog is centered by the user-agent `dialog { margin: auto }` rule, but the platform `base.css` Preflight ships a universal `* { margin: 0 }` reset that wipes it, leaving the dialog pinned to the top-left. `base.css` does **not** re-assert it, so every theme that uses `<dialog>` modals **must** add `dialog { margin: auto }` to its own `assets/css/storefront.css` (an element selector outranks the `*` reset, and the theme stylesheet loads after `base.css`). The default theme ships exactly this rule.

> **Forms inside a modal.** HTML forbids nested `<form>` elements, so a `<dialog>` that contains `@storefrontForm` blocks must be rendered **outside** every other form. The default `pages/checkout.blade.php` does exactly this: its "Manage addresses" pop-ups (a `<dialog>` per address kind, holding the *set default* and *add new address* forms) are emitted **after** `@endstorefrontForm`, alongside the coupon forms — never inside the checkout form. Each modal form carries a relative `redirect` back to the checkout (`/{{ $locale }}/checkout`) and submits as a normal POST (no JS required); with JS the trigger simply opens the dialog in place.

### JavaScript events

The runtime dispatches `CustomEvent`s on `document` so a theme can build a cart drawer, custom badge, etc.:

| Event                          | `detail`                     | Fires when                       |
| ------------------------------ | ---------------------------- | -------------------------------- |
| `storefront:cart:added`        | `{ cart, sections, added, type }` | a `cart-add` **or** `cart-bulk-add` succeeds |
| `storefront:cart:updated`      | `{ cart, sections, type }`        | any other cart mutation succeeds |
| `storefront:cart:error`        | `{ errors, message, type }`       | a mutation is rejected           |
| `storefront:sections:rendered` | `{ sections }`                    | after sections are swapped       |
| `storefront:variant:selected`  | `{ productId, variantId, cart }`  | after a variant re-renders `product-details` |
| `storefront:favorite:toggled`  | `{ productId, active, listId }`   | a `favorite-toggle` succeeds — update heart icons / counts |
| `storefront:color-scheme`      | `{ scheme }`                      | the light/dark scheme changes (`'light'`/`'dark'`) — see §11.10 |

`cart` is `{ item_count, subtotal, discount, surcharge, tax, grand_total, coupon, currency }`. On `storefront:cart:added`, `added` is the just-added line(s) — a list of `{ id, name, sku, image, quantity }` (`null` on every other event) — ready for an add-to-cart confirmation (see *Added-to-cart confirmation* below). Bulk add (`cart-bulk-add`) fires the same `storefront:cart:added` event with all added rows.

```blade
@push('scripts')
<script type="module">
    document.addEventListener('storefront:cart:added', (e) => {
        // e.detail.cart.item_count, e.detail.sections, …
        const drawer = document.querySelector('[data-my-drawer]');
        if (drawer) drawer.classList.add('is-open');
    });
</script>
@endpush
```

### Added-to-cart confirmation (optional)

The default theme shows a confirmation dialog after an item is added to the cart. It is shipped as `partials/added-to-cart-modal.blade.php` (a single native `<dialog>` plus a colocated inline module) and included from `layouts/shop.blade.php` via `@include('partials.added-to-cart-modal')`. There is **no** platform modal you must adopt — override the partial in your theme for a drawer or toast, or omit the `@include` from your layout to suppress the confirmation entirely. The whole feature rides on the `storefront:cart:added` event:

- `event.detail.added` is the just-added line(s): a list of `{ id, name, sku, image, quantity }` (`image` is a pre-sized URL or `null`). It is present only on `cart-add` (other cart events carry `added: null`).
- Open your own UI from it and persist any “don’t show again” choice yourself — the default theme uses a session-scoped `sessionStorage` flag.

```blade
@push('scripts')
<script type="module">
    document.addEventListener('storefront:cart:added', (e) => {
        const added = e.detail?.added;
        if (!Array.isArray(added) || added.length === 0) return;
        // added[0] = { id, name, sku, image, quantity } — render your dialog/drawer.
    });
</script>
@endpush
```

It degrades gracefully: with JS off the add still works (PRG redirect) and nothing opens. A `<dialog>` opened with `showModal()` is centered by the `dialog { margin: auto }` rule every modal theme already ships (see **Modals** in §9).

### `window.Storefront` API

| Method                       | Purpose                                                                      |
| ---------------------------- | ---------------------------------------------------------------------------- |
| `Storefront.config`          | The bootstrap config (`locale`, `currency`, `cartCount`, `routes`, …).        |
| `Storefront.refresh(ids?, params?)` | Re-fetch + swap sections (defaults to those on the page). `params` appends extra query args, e.g. `{ product, variant }` for `product-details`; returns a Promise. |
| `Storefront.selectVariant(productId, variantId)` | Re-render the whole `product-details` section for a variant — dims it while loading, sets `?variant=<id>`, emits `storefront:variant:selected`; returns a Promise. |
| `Storefront.submit(form)`    | Submit a form element through the AJAX flow.                                  |
| `Storefront.toast(msg, kind)`| Show a toast (`kind` = `success` / `error` / `info`).                         |
| `Storefront.setBusy(el, busy?)`| Toggle the busy spinner on any element (`busy` defaults to `true`) — use for your own async actions (§9.9). |
| `Storefront.progress`        | Top loading bar: `Storefront.progress.start()` / `.done()` for custom full-page or long-running flows (§9.9). |
| `Storefront.setColorScheme(scheme)` | Set light/dark scheme (`'light'`/`'dark'`), persist the cookie, update `<html>`, and emit `storefront:color-scheme`. See §11.10. |
| `Storefront.toggleColorScheme()` | Flip between light and dark (convenience wrapper around `setColorScheme`). Wire it to the `color-scheme` form buttons for a no-reload toggle. |

### Section Rendering route

`GET /{locale}/sections?sections=mini-cart,cart-summary` returns `{ "sections": { "<id>": "<html>" } }` for any registered ids — the platform analogue of Shopify's Section Rendering API. Use it (via `Storefront.refresh()`) to re-sync cart UI after navigation, pagination or filtering without a reload.

### Adopting AJAX in a custom theme

1. Keep `@storefrontScripts` before `</body>` in your layouts.
2. Wrap the parts you want refreshed in `@storefrontSection(...)` (the ids above).
3. Use `@storefrontForm('cart-*')` for cart actions — they're enhanced automatically.

That's it. The toast styling uses platform utility classes, so toasts work out of the box; restyle them by targeting `.storefront-toast` / `.storefront-toast--success` / `--error` / `--info` in your theme CSS (your stylesheet loads after the platform base, so equal-specificity overrides win).

---

## 9.9 Loading & busy states

The platform makes **every form submission show a loading state automatically** — you write no JavaScript and no markup for it. This rides on the same runtime that powers AJAX cart sections (§9.7), loaded once via `@storefrontScripts`. Good e-commerce UX demands that a shopper always sees that their click registered, because an action (add to cart, log in, place order) can take a moment on the server.

What the visitor sees:

- **A spinner on the button they pressed.** The clicked submit control gets a `.storefront-busy` spinner and its label is hidden while the request is in flight — for both AJAX cart submits *and* full-page form submits (login, register, checkout, account, …). The spinner is drawn by `base.css` in the button's own foreground colour.
- **A top progress bar on full-page submits.** A thin `[data-storefront-progress]` bar climbs across the top of the viewport while the browser navigates, then completes when the new page takes over — the classic "page is loading" hint.
- **Double-submit protection.** The pressed button is disabled until the response (AJAX) or the navigation (full-page) finishes, so an impatient double-click can't fire the action twice. For full-page submits the disable is deferred one tick so the button's `name` / `value` is still submitted.

It degrades gracefully: with JavaScript off, every form still submits the classic way — there is simply no spinner.

### What you must do

Nothing special — just keep to the form contract:

- Use `@storefrontForm($type, …)` for every POST (§9.5). That stamps the `data-storefront-form` id the runtime keys on, so your form is covered automatically.
- Keep the submit control a real `<button type="submit">` or `<input type="submit">` **inside** the form. A `<div>` / `<a>` "button" can't be found, disabled, or spun.
- Always give the button an accessible label (visible text or `aria-label`) — the spinner hides the visible text, and assistive tech reads the form's `aria-busy`.

### Opting out

Add `data-storefront-loading="off"` to a single form to suppress the automatic spinner + progress bar (the form still submits normally). Use this only when you provide your own feedback.

### Loading on link navigations

Forms are covered automatically, but a plain navigation can take a moment too — the cart's **Proceed to checkout** link is the canonical case. Add `data-storefront-loading-link` to a navigating `<a>` and the runtime shows the same affordance the instant it's clicked: a spinner on the link plus the top progress bar, held while the next page loads.

```blade
<a href="@routeUrl('store.checkout')" data-storefront-loading-link class="…">@t('Proceed to checkout')</a>
```

Only an ordinary primary activation qualifies — the runtime leaves modified clicks (⌘/Ctrl/Shift/Alt or middle-click, i.e. open-in-new-tab), `target="_blank"`, `download` links and non-navigating hrefs (`#…`, `javascript:`) alone, so a spinner is never stranded on a page that didn't navigate. Returning via the back/forward cache clears it automatically. It needs no JavaScript from you; with the runtime absent the link just navigates normally.

### Your own async actions (required)

For custom background work in an inline `<script type="module">` (§2.2) — anything that calls an endpoint, waits, or does heavy work — you **must** drive the same busy affordance through the public API so your theme stays consistent and never leaves the UI silent:

| Call                            | Effect                                                              |
| ------------------------------- | ------------------------------------------------------------------ |
| `Storefront.setBusy(el)`        | Show the spinner on `el` (a button, etc.) and hide its label.      |
| `Storefront.setBusy(el, false)` | Clear the busy state.                                              |
| `Storefront.progress.start()`   | Show the top loading bar (e.g. before a manual `location.assign`). |
| `Storefront.progress.done()`    | Complete and hide the bar.                                         |

Always pair them with `try` / `finally` so the spinner clears even on error, and guard with optional chaining so the page still works if the runtime is absent:

```blade
<button type="button" data-newsletter-submit>@t('Subscribe')</button>

<script type="module">
    for (const btn of document.querySelectorAll('[data-newsletter-submit]')) {
        btn.addEventListener('click', async () => {
            window.Storefront?.setBusy(btn);
            try {
                await fetch('/newsletter', { method: 'POST' });
                window.Storefront?.toast('Subscribed', 'success');
            } catch {
                window.Storefront?.toast('Something went wrong', 'error');
            } finally {
                window.Storefront?.setBusy(btn, false);
            }
        });
    }
</script>
```

#### Section refreshes (`Storefront.refresh()`)

`Storefront.refresh()` swaps section HTML but shows **no loading state of its own** — you must add one. The recommended pattern: guard with `if (!api) return` (cleaner than chaining `?.` on the returned Promise), start the top progress bar, dim the target section's opacity, then clear both in `.finally()` so they always reset whether the fetch succeeded or failed:

```blade
<script type="module">
    function reloadSection(sectionId, params) {
        const api = window.Storefront;
        if (!api) return;

        const section = document.querySelector(`[data-storefront-section="${sectionId}"]`);
        api.progress.start();
        if (section) section.style.opacity = '0.5';

        api.refresh([sectionId], params).finally(() => {
            api.progress.done();
            if (section) section.style.opacity = '';
        });
    }
</script>
```

- Use **`.finally()`**, not `.then()` + `.catch()` separately — it fires on both resolve and reject, so the loading state is always cleared even when the network request fails.
- **Opacity `0.5`** signals "stale, updating" without hiding content. Adjust in your theme CSS if you prefer a different treatment (e.g. a spinner overlay via `position: relative` + a `::before` pseudo-element).
- The pattern above is what the default theme uses for the checkout shipping-method summary refresh (see `pages/checkout.blade.php`).

### Styling

The spinner and bar are platform-owned but fully restyleable: your theme stylesheet loads after `base.css`, so equal-specificity overrides win. Target `.storefront-busy` (and its `::after` spinner) or `[data-storefront-progress]` in `assets/css/storefront.css`. The bar uses your `--color-primary` token by default, so it already matches a re-skinned theme. Motion is suppressed under `prefers-reduced-motion`.

---
