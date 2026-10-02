# Theme contract changelog

> **Latest version.** This copy shipped with your theme download and may be outdated.
> The authoritative, always-current changelog is online:
> https://b2bware.documentationai.com/changelog

This file tracks changes to the **theme authoring contract** (directives, form types, `$store`
keys, canonical surface, tokens). It is not the platform-wide release log. Dates are UTC.

## 2026-10-01 — CAPTCHA on storefront forms

- **New directive `@storefrontCaptcha`** — place the tenant's CAPTCHA widget at an exact spot
  inside a `@storefrontForm`. Entirely optional: a protected form that omits it gets the widget
  injected just before `</form>`, and using the directive suppresses that injection so the
  widget never renders twice. See `blade-api.md` and `forms.md`.
- **New `$store['captcha']`** — client-safe configuration (`enabled`, `provider`, `site_key`,
  `token_input`, `protected_forms`) for themes that want to render their own copy around the
  widget. The secret key stays server-side.
- **The provider script loads through `@storefrontScripts`.** A layout without it cannot submit
  a protected form.
- Tenants choose which of `login`, `register`, `forgot-password`, `reset-password`,
  `verify-email`, `resend-verification` and `cms-form` to protect; verification is server-side,
  and the failure message renders inside the widget wrapper. No theme change is required.
## 2026-09-22 — Default catalog sort

- **`$sort` on All Products and category listings** may be `<attribute_code>` or `-<attribute_code>` when the store has a default sorting attribute and the URL has no `sort`. Direction follows the store setting (ascending unless set to descending). An explicit `sort` query, including `relevance`, is unchanged. No new `$store` key.

## 2026-08-18 — Parent category branch display mode

- **New `$store` key:** `branch_display_mode` (`children` default | `products` | `both`) — store-wide default for how parent categories with children render.
- **Category page view data:** `$branchDisplayMode`, `$showChildren`, `$showProducts`. Themes must branch on these (not `$isLeaf` alone). When products show on a branch, the listing uses descendant-aware `anchor_category_id` filtering.
- **Per-category override:** ProductHub `Category.branch_display_mode` (`null` = inherit store default).
- See `catalog.md` and `view-data.md`.

