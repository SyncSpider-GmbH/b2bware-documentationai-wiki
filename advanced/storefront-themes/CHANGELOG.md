# Theme contract changelog

> **Latest version.** This copy shipped with your theme download and may be outdated.
> The authoritative, always-current changelog is online:
> https://b2bware.documentationai.com/changelog

This file tracks changes to the **theme authoring contract** (directives, form types, `$store`
keys, canonical surface, tokens). It is not the platform-wide release log. Dates are UTC.

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

## 2026-08-18 — Parent category branch display mode

- **New `$store` key:** `branch_display_mode` (`children` default | `products` | `both`) — store-wide default for how parent categories with children render.
- **Category page view data:** `$branchDisplayMode`, `$showChildren`, `$showProducts`. Themes must branch on these (not `$isLeaf` alone). When products show on a branch, the listing uses descendant-aware `anchor_category_id` filtering.
- **Per-category override:** ProductHub `Category.branch_display_mode` (`null` = inherit store default).
- See `catalog.md` and `view-data.md`.

