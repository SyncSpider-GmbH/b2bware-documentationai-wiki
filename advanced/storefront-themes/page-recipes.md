---
title: Page recipes
description: "Per-page view-data contracts: checkout, proposal-preview, account, auth, customer-selection."
---

<Info>
This page also ships inside the default theme download under `docs/10-page-recipes.md`, so offline and AI-assisted authors have the same contract locally. This online version is always the latest.
</Info>

## §10. Page recipes

This page gathers the **per-page contracts** — the extra view data a specific fixed page
receives on top of the globals in [`04-view-data.md`](/advanced/storefront-themes/view-data). Every page also gets the
global variables (`$locale`, `$me`, `$store`, `$cart`, `$messages`, `$localeOptions`, …); only the
page-specific additions are listed here. Pages not listed below render with globals only (e.g.
`not-found` and `error` — see §2.1 / §2.2 in [`00-hard-rules.md`](/advanced/storefront-themes/hard-rules)).

### 10.1 `pages/proposal-preview.blade.php`

The proposal review/accept page. It serves **three modes** from one template, so branch on the
flags rather than assuming a single layout:

| Mode | Trigger | What to render |
| --- | --- | --- |
| Signed-in review | default (customer-scoped) | Read-only proposal; offer **Accept** (`proposal-accept` form, §9.5) which clones the quote into the customer's cart. |
| Anonymous public order | `$editable === true` (public token, customer assigned) | Standalone document (`$hideChrome === true`); wrap the lines in a `proposal-public-order` form so the visitor can tune quantities and order directly. Pass `'_params' => ['token' => $proposalId]`. |
| Post-order thank-you | `$orderedId` is set | Confirmation state only (no login); show the order number. |
| Theme-editor / admin preview | `$readOnly === true` | Exactly what the customer sees, but **no** actionable form. |

**View data:**

| Variable | Type | Meaning |
| --- | --- | --- |
| `$proposal` | object | The quote/proposal. `$proposal->description` is admin-authored rich text — render with `{!! !!}` inside `.storefront-richtext`. |
| `$proposalId` | string | Route id; also the `token` for the public-order form. |
| `$proposalTitle` | string\|null | Plain-text title for `@section('title', …)`. |
| `$isPublic` | bool | Anonymous token holder rather than the signed-in owner. |
| `$canPublicOrder` | bool | Public proposal has a customer assigned and can be ordered directly. |
| `$editable` | bool | Visitor may edit quantities before ordering (equals `$canPublicOrder`). |
| `$readOnly` | bool | Signed admin preview — render, but don't offer any form. |
| `$orderedId` | string\|null | Set after a successful anonymous order → render the thank-you state. |
| `$hideChrome` | bool | `true` for the standalone share document (order/thank-you). Wrap chrome in `@unless($hideChrome ?? false)`; the default `shop.blade.php` already does. |
| `$groups` | Collection | Display groups. Each: `name`, `description` (rich text), `image`, `items` (each item has product info + `quantity`). Ungrouped items fall into a trailing unnamed bucket. |
| `$previewLines` | array | Flat line rows behind the grouped view. |
| `$totals` | array | Keys: `subtotal`, `discount`, `surcharge`, `shipping`, `tax`, `grand_total`. |

Errors flash back via `@storefrontError('proposal')`, `@storefrontError('items')`,
`@storefrontError('accept_terms')`. Owner-authored CMS content renders through
`@storefrontSlot('content-top')` (see §9.16 in [`09-analytics-slots.md`](/advanced/storefront-themes/analytics-and-slots)).

### 10.2 `pages/checkout.blade.php`

Wraps the `checkout` form (§9.5). Renders the address pickers via
`partials/checkout-address-option` / `checkout-address-summary` and the totals via the
`checkout-summary` AJAX section (§9.7). Because HTML forbids nested `<form>`s, emit the
"Manage addresses" `<dialog>` blocks **outside** the checkout form (see the modal note in
[`05-ajax-runtime.md`](/advanced/storefront-themes/ajax-and-runtime)). Coupons use `cart-coupon-apply` /
`cart-coupon-remove`, gated on `checkout.enable_coupons` (§9.6).

### 10.3 `pages/guest-order.blade.php`

Order confirmation for guest checkouts, reachable via a signed URL (bookmarkable without login).
View data: `$order` (object or null), `$orderId` (string), `$orderItems` (Collection),
`$orderTotals` (array: `subtotal`, `shipping`, `discount`, `tax`, `grand_total`).

### 10.4 `pages/customer-selection.blade.php`

Agent/impersonation flow: renders the `customer-selection` form (fields `customer_id`, optional
`redirect`). Only reached when the visitor is an agent; pairs with the impersonation banner
(`$isImpersonating`, §9.6) and the `impersonation-leave` form.

### 10.5 Account pages (`pages/account/*`)

All account pages receive the signed-in customer plus page-specific collections. Use
`partials/account-nav` (pass `active`) for the sidebar. Highlights:

- `account/order.blade.php` — order detail; use `orderStatusLabel()` / `orderStatusTone()` (§9)
  for the status badge, and the `reorder` form when the order is completed and reorder is enabled.
- `account/shipping-addresses.blade.php` / `account/billing-addresses.blade.php` — both render
  `partials/account-addresses-page`; use the `address-shipping-*` / `address-billing-*` forms.
- `account/quick-order.blade.php` — only when `$store['quick_order_enabled']`; `quick-order-upload`
  + `quick-order-add` forms (§9.5).
- `account/catalog-export.blade.php` — only when `$store['catalog_export_enabled']`; the
  `catalog-export*` forms and the `catalog-export-preview` AJAX section.
- `account/api-keys.blade.php` — `api-key-create` / `api-key-revoke`; the one-time plaintext token
  arrives as `$newApiKeyToken` for a single render only.

### 10.6 Auth pages (`pages/login|register|forgot-password|reset-password|verify-email`)

These use the `auth` layout (which honours `$store['login_background']`) and the matching auth
forms (§9.5). Render the password checklist from `$passwordRequirements` / `$passwordRules`
(§9.6) on register and reset-password.
