# Theme contract changelog

> **Latest version.** This copy shipped with your theme download and may be outdated.
> The authoritative, always-current changelog is online:
> https://b2bware.documentationai.com/changelog

This file tracks changes to the **theme authoring contract** (directives, form types, `$store`
keys, canonical surface, tokens). It is not the platform-wide release log. Dates are UTC.

## 2026-10-08 — `@storefrontImage` hard rule + desk media + Bunny API notes

- **Hard rule** (also in `hard-rules.md` §9): every catalog / customer `media_url` in an
  `<img src>` **must** use `@storefrontImage(...)`. Raw Bunny or SpiderDesk media URLs fail
  review.
- **Platform:** `@storefrontImage` now appends sizing params for the SpiderDesk / user-service
  host (`USER_SERVICE_BASE_URL`) as well as Bunny `*.b-cdn.net` / configured pull zones — so
  desk `/media/...` tiles resize for every tenant, not only Bunny-hosted media.
- **Docs:** `seo-and-images.md` §9.11 documents the platform subset (`width`, `height`,
  `quality`, `aspect_ratio`) and the broader Bunny Dynamic Images API (crop, format, filters,
  …) for author reference.

## 2026-10-01 — Category UI type in the header

- **`$store['category_ui_type']`** (`list` default | `mega_menu`) and **`$store['mega_menu_depth_start']`** (`0` default) drive the header category nav. `list` links to the categories index. `mega_menu` opens `$megaMenuCategories` (that depth and the next). See `view-data.md`.
- Default theme: `partials/nav.blade.php`. `$rootCategories` is unchanged (footer, catalog export).

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

## 2026-09-21 — Incoming stock on the product page

- **`$stockInfo.incoming`** (and `$variantRows[*].stock.incoming`): list of
  `{ quantity, date, undated }` when ProductHub **Show incoming on storefront** is on.
  Quantity on `$stockInfo` is **buyable**, not raw on-hand. Catalog `in_stock` filters
  `stock.buyable_qty > 0`. See `view-data.md` (`$stockInfo`) and `catalog.md`.
- Default theme: simple English `@t('Incoming')` list on `partials/product-details.blade.php`.
  Switch off → no incoming in theme data.

## 2026-09-04 — Address country is a select

- **New helpers:** `storefront_countries()` (canonical `['name','iso2','iso3']` list, sorted by
  name) and `storefront_country_name($value)` (resolve a name/ISO2/ISO3 value to its canonical
  name for preselecting an `<option>`) — see `blade-api.md` §9.
- **Address `country` is now a `<select>`** in the account address form, checkout (billing +
  shipping) and the registration company block, built from `storefront_countries()`. The server
  validates it with the `ValidCountry` rule (accepts name, ISO2 or ISO3); the stored value is the
  country **name**. Do not render `country` as a free-text input — see `forms.md` §9.5.

## 2026-08-31 — Pricing rendering contract

- **New doc:** `pricing.md` (§9.16) — the single source of truth for price resolution and the
  per-surface rendering matrix (catalog card / product detail / cart line). Matrix rows are
  asserted by platform tests.
- **`priceViews` / `priceView` behaviour:** `compare_excl` / `compare_incl` are now populated
  for **every** discount type (group, company-group, 1+ tier, catalog rule, ERP provider) —
  previously only date-windowed special prices produced a compare-at. Catalog listings also
  stack catalog price rules, so the displayed price always equals the cart charge.
- **Cart lines:** `original_price_*` / `has_discount` now baseline on the regular list price,
  so tier- and contract-priced lines report a discount.
- **Product page:** `$tierPrices` now excludes tiers equal to the displayed unit price (a 1+
  tier is the base price, not a volume discount). `$contractPrice` is unchanged in shape; the
  default theme renders it as a label-only badge inside the main price block instead of a
  separate box.
- **List view (default theme):** rows emit `data-line-original-unit` + `data-tier-prices`;
  the live total is tier-aware and shows a struck original total when discounted.

## 2026-08-24 — Graceful account deletion (grace period)

- **`profile-delete` behaviour change:** no longer deletes immediately — it now *requests* deletion
  (still takes `current_password`) and emails a 6-digit confirmation code.
- **New form types:** `profile-delete-confirm` (`token`, 6 digits) and `profile-delete-cancel`.
- **New profile page view data:** `$deletionRequest` (`null` or
  `{status: 'awaiting_confirmation'|'scheduled', scheduled_for, expires_at, grace_days, …}`).
  After confirmation the account is soft-deleted only once the grace period (default 14 days)
  elapses; the customer can cancel during that window.
- See `forms.md` and `page-recipes.md` §10.5.

## 2026-08-18 — Parent category branch display mode

- **New `$store` key:** `branch_display_mode` (`children` default | `products` | `both`) — store-wide default for how parent categories with children render.
- **Category page view data:** `$branchDisplayMode`, `$showChildren`, `$showProducts`. Themes must branch on these (not `$isLeaf` alone). When products show on a branch, the listing uses descendant-aware `anchor_category_id` filtering.
- **Per-category override:** ProductHub `Category.branch_display_mode` (`null` = inherit store default).
- See `catalog.md` and `view-data.md`.

