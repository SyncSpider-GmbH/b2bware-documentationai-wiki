---
title: Page recipes
description: Per-page view-data contracts: checkout, proposal-preview, account, auth, customer-selection.
---

## §10. Page recipes

This page gathers the **per-page contracts** — the extra view data a specific fixed page
receives on top of the globals in [`view-data.md`](view-data.md). Every page also gets the
global variables (`$locale`, `$me`, `$store`, `$cart`, `$messages`, `$localeOptions`, …); only the
page-specific additions are listed here. Pages not listed below render with globals only (e.g.
`not-found` and `error` — see §2.1 / §2.2 in [`hard-rules.md`](hard-rules.md)).

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
`@storefrontSlot('content-top')` (see §9.16 in [`analytics-and-slots.md`](analytics-and-slots.md)).

### 10.2 `pages/checkout.blade.php`

Wraps the `checkout` form (§9.5). Renders the address pickers via
`partials/checkout-address-option` / `checkout-address-summary` and the totals via the
`checkout-summary` AJAX section (§9.7). Because HTML forbids nested `<form>`s, emit the
"Manage addresses" `<dialog>` blocks **outside** the checkout form (see the modal note in
[`ajax-and-runtime.md`](ajax-and-runtime.md)). Coupons use `cart-coupon-apply` /
`cart-coupon-remove`, gated on `checkout.enable_coupons` (§9.6).

`$defaultBillingMethodId` is the shopper's customer, company, or group default when that
method is visible, otherwise the store fallback (`$store['default_billing_method_id']`)
when that method is visible for them, otherwise empty. Two render states:

- `$store['hide_payment_method']` and a resolved `$defaultBillingMethodId`: no Payment
  method block and no payment-method dialogs. Submit `<input type="hidden" name="billing_method_id">`.
- Otherwise: the radio list, pre-checked with `$defaultBillingMethodId`. This includes
  Hide ticked when nothing resolved — the shopper still chooses.

Hide does not lock the method. Send `billing_method_id` with the checkout-summary refresh,
including the hidden input, the same way shipping is sent.

### 10.3 `pages/guest-order.blade.php`

Order confirmation for guest checkouts, reachable via a signed URL (bookmarkable without login).
View data: `$order` (object or null), `$orderId` (string), `$orderItems` (Collection),
`$orderTotals` (array: `subtotal`, `shipping`, `discount`, `tax`, `grand_total`).

### 10.4 `pages/customer-selection.blade.php`

Sales agents pick who to order for. The page opens on company search. A Company / User
switch on the same page changes the search. The `customer-selection` form still posts
`customer_id` and optional `redirect` to `store.customer-selection.post`. There is no company session.

Query string: `mode` (`company` by default, or `user`), `q`, `company` (drill into one company's
users), and `redirect`. Switching mode drops `company` and keeps `q` and `redirect`.

View data, in addition to `$agent`, `$selectedCustomer`, `$isImpersonating`, `$redirectTo`, and `$search`:

| Key | Meaning |
|-----|---------|
| `$searchMode` | `company` or `user`. |
| `$companies` | Paginator of company rows on the company search step. Empty on the user step and the drill-in. |
| `$selectedCompany` | The company being drilled into, or null. |
| `$customers` | Users for user mode and for the company drill-in. On the company search step, still the flat user list that matches `q` (including a company-name match), so a theme that overrides this page and only loops `$customers` keeps showing people. |

A company row has `id`, `name`, `company_number`, `email`, `user_count`, and `user`. `user` is the one eligible person (`id`, `name`, `email`, `customer_number`) or null when the company has several. One user submits that `customer_id`. Several users link to `?company={id}` so the agent picks one.

An eligible user has role type `user`, is not the agent, and is not blocked by an inactive company. A company with no eligible user is omitted. An inactive company is omitted. An agent with a `company_id` only sees that company. A global agent sees every eligible company. Users with no company stay in user search for a global agent.

Override sections stay `customer-selection.search` and `customer-selection.list`. A theme that replaces the whole `pages/customer-selection.blade.php` keeps the people list from `$customers` until that copy is updated. Pairs with the impersonation banner (`$isImpersonating`, §9.6) and the `impersonation-leave` form.

### 10.5 Account pages (`pages/account/*`)

All account pages receive the signed-in customer plus page-specific collections. Use
`partials/account-nav` (pass `active`) for the sidebar. Highlights:

- `account/order.blade.php` — order detail; use `orderStatusLabel()` / `orderStatusTone()` (§9)
  for the status badge, the populated custom order attributes in `$order->attributeValues`, and the
  `reorder` form when the order is completed and reorder is enabled. `$orderAttributeCodes` is a
  map of populated custom attribute codes, for suppressing a legacy native field with the same code.
- `account/shipping-addresses.blade.php` / `account/billing-addresses.blade.php` — both render
  `partials/account-addresses-page`; use the `address-shipping-*` / `address-billing-*` forms.
- `account/quick-order.blade.php` — only when `$store['quick_order_enabled']`; `quick-order-upload`
  + `quick-order-add` forms (§9.5).
- `account/catalog-export.blade.php` — only when `$store['catalog_export_enabled']`; the
  `catalog-export*` forms and the `catalog-export-preview` AJAX section.
- `account/api-keys.blade.php` — `api-key-create` / `api-key-revoke`; the one-time plaintext token
  arrives as `$newApiKeyToken` for a single render only.
- `account/profile.blade.php` — receives `$deletionRequest` (`null` or
  `{status: 'awaiting_confirmation'|'scheduled', scheduled_for, expires_at, grace_days, …}`), which
  drives the account-deletion danger zone: no request → `profile-delete` form (password + emailed
  code), awaiting confirmation → `profile-delete-confirm` (6-digit `token`) + `profile-delete-cancel`,
  scheduled → banner with the deletion date + `profile-delete-cancel` (§9.5).

### 10.6 Auth pages (`pages/login|register|forgot-password|reset-password|verify-email`)

These use the `auth` layout (which honours `$store['login_background']`) and the matching auth
forms (§9.5). Render the password checklist from `$passwordRequirements` / `$passwordRules`
(§9.6) on register and reset-password.
