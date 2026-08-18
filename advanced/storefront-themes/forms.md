---
title: Forms
description: "The @storefrontForm contract and the full registry of platform form types."
---

<Info>
This page also ships inside the default theme download under `docs/03-forms.md`, so offline and AI-assisted authors have the same contract locally. This online version is always the latest.
</Info>

## 9.5 Forms — the `@storefrontForm` contract

Themes **never** write a route name into a `<form action>` and **never** hand-roll `@csrf`. Use the `@storefrontForm($type, $attrs = [])` / `@endstorefrontForm` directive pair: pick a stable form-type identifier, and the platform emits the correct opening tag, CSRF token, and a hidden `redirect` field automatically.

This is the same contract Shopify uses for `{% form 'customer_login' %}`: the **platform owns the endpoint name → route mapping**, and the **theme owns the markup and field names**.

### Allowed form types

| `$type`                | Route                          | Required field names                                                 |
| ---------------------- | ------------------------------ | -------------------------------------------------------------------- |
| `login`                | `store.login.post`             | `email`, `password`                                                  |
| `logout`               | `store.logout.post`            | _(none — confirmation only)_                                         |
| `register`             | `store.register.post`          | `email`, `password`, `password_confirmation`, `first_name`, `last_name`, plus `company_*` fields when `register.company.required` is on |
| `forgot-password`      | `store.forgot-password.post`   | `email`                                                              |
| `reset-password`       | `store.reset-password.post`    | `email`, `token`, `password`, `password_confirmation`                |
| `verify-email`         | `store.verify-email.post`      | `email`, `code` (6 digits)                                           |
| `resend-verification`  | `store.resend-verification.post` | `email`                                                            |
| `cart-add`             | `store.cart.add.post`          | `product_id`, `quantity` (optional `variant_id`, `redirect`) — gate on `$canAddToCart`, see §9.6 |
| `cart-bulk-add`        | `store.cart.bulk-add.post`     | `items[<product_id>]` = quantity per row (zeros skipped) — bulk add of configurable variants with partial success; gate on `$canSeePrices && $canAddToCart`, see *Configurable products (variants)* |
| `cart-update`          | `store.cart.update.post`       | `quantity` — pass `'_params' => ['cartItem' => $item->id]` in `$attrs` |
| `cart-line-delivery-date` | `store.cart.delivery-date.post` | `delivery_date` (nullable, empty clears) — pass `'_params' => ['cartItem' => $item->id]`; only render when `$store['delivery_date_enabled']` |
| `cart-remove`          | `store.cart.remove.post`       | _(none)_ — pass `'_params' => ['cartItem' => $item->id]` in `$attrs` |
| `cart-clear`           | `store.cart.clear.post`        | _(none)_                                                             |
| `cart-coupon-apply`    | `store.cart.coupon.apply.post` | `coupon_code` (only rendered when `checkout.enable_coupons` is on)   |
| `cart-coupon-remove`   | `store.cart.coupon.remove.post`| _(none)_                                                             |
| `profile-delete`       | `store.account.profile.delete.post` | `current_password` — permanently closes the signed-in account (confirmation modal) |
| `quick-order-upload`   | `store.account.quick-order.upload` | `file` (CSV, `SKU,Quantity`) — multipart; pass `'enctype' => 'multipart/form-data'`. With JS the theme posts it as JSON and merges the returned rows into the shared review table; with JS off it re-renders the page with the server-seeded review table. Only reachable when `$store['quick_order_enabled']`. |
| `quick-order-add`      | `store.account.quick-order.add`  | `sku[]`, `quantity[]` (parallel arrays) — confirms the reviewed rows into the cart (SKUs are re-resolved server-side under the customer's visibility scope). Used by both the CSV review table and the client-side typeahead order review. Only reachable when `$store['quick_order_enabled']`. |
| `catalog-export`       | `store.account.catalog-export.post` | `columns[]` (product field keys, submitted in display order), `format` (`csv`/`xlsx`/`pdf`/`xml`), plus the shared native product filters `q` (search), `category`, `price_min`, `price_max`, `in_stock`, `sort` — generates the customer's single stored export (a frozen snapshot) and redirects back to the page, replacing any previous file. Only rendered when `$store['catalog_export_enabled']`. When the `customer-sku-module` app is installed for the tenant, an extra `customer_ref` ("Customer SKU") column is offered right after `sku`, pre-checked by default, filled with the signed-in customer's own reference (never another customer's) |
| `catalog-export-rotate` | `store.account.catalog-export.rotate.post` | _(none)_ — regenerates the share token, moving the stored file under a fresh URL so the previously copied link returns 404. Keeps the file |
| `catalog-export-delete` | `store.account.catalog-export.delete.post` | _(none)_ — deletes the stored file and its share link (public URL returns 404) so the customer can start fresh |
| `api-key-create`        | `store.account.api-keys.post` | `name` (required), `expires_at` (optional, date-only, must be after today) — creates a new API key and flashes its one-time plaintext token to the session for a single render on the api-keys page |
| `api-key-revoke`        | `store.account.api-keys.revoke.post` | _(none)_ — revokes (deletes) the API key identified by the `id` route param; the key stops working immediately |
| `reorder`              | `store.account.order.reorder.post`         | _(none — order id supplied via `_params`)_ — pass `'_params' => ['order' => $order->id]` in `$attrs`. Only rendered when `($order->status ?? '') === 'completed' && ($store['reorder_enabled'] ?? true)`. Redirect lands on the **cart page** with `$messages['success']` (items added), `$messages['info']` (custom-item skip warning or nothing-added notice), or `$messages['error']` (order not found / not completed). Both success and info may appear together for a mixed order. See _Reorder entry-point pattern_ below. |
| `color-scheme`         | `store.color-scheme.set`       | `scheme` (`light`/`dark`) — light/dark preference toggle; persists the `storefront_color_scheme` cookie. Render as two scheme buttons and enhance with `Storefront.toggleColorScheme()`. See §11.10 |
| `cms-form`             | `store.form.submit.post`       | `form_key`, `fields[<name>]` per field — the builder form widget; stored as a submission, honeypot `_hp` and optional `_success` message. Public (guests + customers). |

### Checkout, account, address, favorites, proposal & agent forms

These complete the registry. Every type below is a real, platform-owned POST route — pick the type, own the markup and field names.

| `$type`                     | Route                                          | Notes                                                                                     |
| --------------------------- | ---------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `checkout`                  | `store.checkout.post`                          | Complete checkout. Rendered on `pages/checkout.blade.php`; carries the selected shipping/billing method + address ids and any `checkout_attributes`. See §10 page recipes. |
| `profile`                   | `store.account.profile.post`                   | Update the signed-in customer profile (name, phone, etc.).                                |
| `profile-email-request`     | `store.account.profile.email.request.post`     | Start an email-change (sends confirmation). `email` (new address).                        |
| `profile-email-confirm`     | `store.account.profile.email.confirm.post`     | Confirm the pending email change. `code`/`token`.                                         |
| `profile-email-cancel`      | `store.account.profile.email.cancel.post`      | Cancel a pending email change. _(none)_                                                   |
| `address-shipping-create`   | `store.account.address.shipping.create.post`   | Create a shipping address (fields from `partials/account-address-form.blade.php`).        |
| `address-shipping-update`   | `store.account.address.shipping.update.post`   | Update; pass `'_params' => ['address' => $address->id]`.                                  |
| `address-shipping-delete`   | `store.account.address.shipping.delete.post`   | Delete; `'_params' => ['address' => $address->id]`.                                       |
| `address-shipping-default`  | `store.account.address.shipping.default.post`  | Mark default; `'_params' => ['address' => $address->id]`.                                 |
| `address-billing-create`    | `store.account.address.billing.create.post`    | As shipping, for billing.                                                                 |
| `address-billing-update`    | `store.account.address.billing.update.post`    | `'_params' => ['address' => $address->id]`.                                               |
| `address-billing-delete`    | `store.account.address.billing.delete.post`    | `'_params' => ['address' => $address->id]`.                                               |
| `address-billing-default`   | `store.account.address.billing.default.post`   | `'_params' => ['address' => $address->id]`.                                               |
| `favorite-toggle`           | `store.favorites.toggle.post`                  | Add/remove a product from the active favorites list. `product_id`. Fires `storefront:favorite:toggled` (§9.7). |
| `favorite-list-create`      | `store.favorites.list.create.post`             | `name`.                                                                                   |
| `favorite-list-rename`      | `store.favorites.list.rename.post`             | `name`; `'_params' => ['list' => $list->id]`.                                             |
| `favorite-list-delete`      | `store.favorites.list.delete.post`             | `'_params' => ['list' => $list->id]`.                                                     |
| `favorite-list-select`      | `store.favorites.list.select.post`             | Switch the active favorites list; `'_params' => ['list' => $list->id]`.                   |
| `proposal-accept`           | `store.proposal.accept.post`                   | Signed-in customer accepts a proposal. `'_params' => ['proposal' => $proposalId]`. See §10 page recipes. |
| `proposal-public-order`     | `store.proposal.public.order.post`             | Anonymous public proposal share page orders directly (standalone/`$hideChrome`). `'_params' => ['token' => $token]`. |
| `customer-selection`        | `store.customer-selection.post`                | Agent/impersonation: pick which customer to act as. `customer_id`, optional `redirect`. Rendered on `pages/customer-selection.blade.php`. |
| `impersonation-leave`       | `store.impersonation.leave.post`               | Agent leaves the impersonated session. _(none)_ Rendered from `partials/impersonation-banner.blade.php`. |

Unknown types render an inert `<form action="#" data-storefront-form-error="unknown-type:…">` so the page still loads; check the rendered HTML if a submit does nothing.

### Minimal example

```blade
@storefrontForm('login', ['class' => 'login__form flex flex-col gap-4'])
    <input type="email"    name="email"    value="{{ old('email') }}" required autofocus>
    @storefrontError('email')

    <input type="password" name="password" required>
    @storefrontError('password')

    <button type="submit">@t('Login')</button>
@endstorefrontForm
```

### Rules

- **Never echo passwords via `old(...)`** — keep `<input type="password">` empty on re-render.
- **Use `old(...)` for every non-password field** so the form survives validation re-renders.
- **Inline errors:** call `@storefrontError('field_name')` directly under each input. The directive emits `<span class="storefront-form-error" data-storefront-form-error="field_name">…</span>` when there's an error, or an empty string otherwise — no `@if` wrapper needed.
- **Messages (flash messages / notices / alerts):** read from the `$messages` global (see §9.6) — `$messages['success']`, `$messages['info']`, `$messages['error']`. These are set by controllers via `redirect()->with('key', ...)` and injected by the platform so themes never need to call `session()` (a forbidden helper). **Always echo with `{{ }}`** — values may contain user-supplied input such as a submitted email address. The `banner` component does exactly that and renders nothing when the message is empty: `@include('components.banner', ['type' => 'success', 'message' => $messages['success'] ?? null])`.
- **Redirects:** pass `?redirect=/some/safe/path` in a query string when linking to `/login`, `/verify-email`, etc. The platform validates it server-side (must be a single-leading-slash same-origin path, no `//`, no scheme) and rejects anything else, so an attacker cannot use it as an open redirect. The form re-emits the validated value as a hidden field so it round-trips through the submit cycle.
- **HTTP method:** always `POST`. The directive ignores any `method` you pass in `$attrs`.
- **CSRF:** automatic — `@csrf` is already emitted, do not add it.
- **No JavaScript required:** every form is a plain HTML POST. The cart forms (`cart-add`, `cart-bulk-add`, `cart-update`, `cart-line-delivery-date`, `cart-remove`, `cart-clear`, `cart-coupon-apply`, `cart-coupon-remove`) are **additionally auto-enhanced to AJAX** when the runtime is present (§9.7) — but that is a progressive enhancement; the plain POST is always the fallback, so themes must work without JS.
- **Loading feedback is automatic:** submitting any storefront form shows a busy spinner on the button that was clicked and — for full-page submits — a top progress bar, and blocks that button from double-submitting until the response/navigation completes. Keep submit controls as real `<button type="submit">` / `<input type="submit">` **inside** the form (a `<div>` / `<a>` can't be found or spun) and always give them an accessible label. Opt a single form out with `data-storefront-loading="off"`. See §9.9.

### Forgot-password & email-verification quirks

- `forgot-password` **always** flashes the same generic "if the email exists…" message regardless of whether the address is on file (account-enumeration defence).
- `resend-verification` follows the same rule — same generic message either way.
- `reset-password` requires both `?token=` and `?email=` in the URL; when either is missing the page renders an "invalid link" variant.

### Reading registration config

The Register page renders extra `company_*` inputs only when the installation requires them. Gate them on the `company_required` flag from `$store` (§9.6) rather than hardcoding:

```blade
@storefrontForm('register', ['class' => 'register__form'])
    {{-- always-on personal fields --}}
    <input type="text" name="first_name" value="{{ old('first_name') }}" required>
    <input type="text" name="last_name"  value="{{ old('last_name') }}"  required>
    <input type="email" name="email"     value="{{ old('email') }}"      required>
    <input type="password" name="password" required>
    <input type="password" name="password_confirmation" required>

    @if($store['company_required'])
        <fieldset class="register__company">
            <legend>@t('Company details')</legend>
            <input type="text" name="company_name"     value="{{ old('company_name') }}" required>
            <input type="text" name="company_vat_id"   value="{{ old('company_vat_id') }}">
            <input type="text" name="company_street"   value="{{ old('company_street') }}" required>
            <input type="text" name="company_postal"   value="{{ old('company_postal') }}" required>
            <input type="text" name="company_city"     value="{{ old('company_city') }}" required>
            <input type="text" name="company_country"  value="{{ old('company_country') }}" required>
        </fieldset>
    @endif

    <button type="submit">@t('Create account')</button>
@endstorefrontForm
```

The server validates the same `register.company.required` flag — if you skip the `@if($store['company_required'])` guard, missing fields will surface as inline validation errors via `@storefrontError(...)`.

Within the company block, **which fields are required** is driven by the CustomerHub `company_required_fields` setting, exposed as `$companyRequiredFields` (see §9.6 globals). Each configurable field (`name`, `phone`, `website`, `vat_number`, `registration_number`, `address`) can be independently required. Add a required marker and `required` HTML attribute like this:

```blade
<label>
    @t('Company name')@if($companyRequiredFields['name'] ?? false)<span aria-hidden="true" class="text-error ml-0.5">*</span>@endif
</label>
<input name="company[name]"
       {{ ($companyRequiredFields['name'] ?? false) ? 'required' : '' }}
       …>
```

The `address` key requires the whole block — apply it to `address_line_1`, `zip`, `city`, and `country` together.

### Reorder entry-point pattern

The `reorder` form type adds the lines from a completed order back to the active cart. Rules:

- **Gate it** on two conditions: `($order->status ?? '') === 'completed'` and `($store['reorder_enabled'] ?? true)`. Never render it for in-flight, cancelled, or unknown-status orders.
- **Supply the order id** via `_params`: `@storefrontForm('reorder', ['_params' => ['order' => $order->id]])`.
- **No form fields** are needed inside the pair — just a `<button type="submit">`.
- **After submit**, the browser lands on the **cart page** (not back on the order page). Display `$messages['success']`, `$messages['info']`, and `$messages['error']` on the cart page as you would on any other page. A mixed order (product-backed + custom lines) produces **both** a success message and an info notice in the same redirect, so render both independently.
- **Custom-only orders** (all lines are manual/custom) produce **only** `$messages['info']` — no green success message. Do not assume a green flash when the customer clicks reorder.
- **Custom item warning text** is localized through the theme translation pipeline and may reference item names the customer entered.
- **Where to place entry points:** the platform default theme exposes three entry points — order detail page header, per-row button on the orders list, and inline icon button on the recent-orders list on the account dashboard. A custom theme may replicate any or all of them using the same `reorder` form type.

Example — minimal reorder button:

```blade
@if(($order->status ?? '') === 'completed' && ($store['reorder_enabled'] ?? true))
    @storefrontForm('reorder', ['_params' => ['order' => $order->id], 'class' => 'inline'])
        <button type="submit" class="btn btn--primary">
            @t('Re-order')
        </button>
    @endstorefrontForm
@endif
```

---
