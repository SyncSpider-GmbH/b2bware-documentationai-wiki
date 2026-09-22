# Theme contract changelog

> **Latest version.** This copy shipped with your theme download and may be outdated.
> The authoritative, always-current changelog is online:
> https://b2bware.documentationai.com/changelog

This file tracks changes to the **theme authoring contract** (directives, form types, `$store`
keys, canonical surface, tokens). It is not the platform-wide release log. Dates are UTC.

## 2026-09-22 — Default catalog sort

- **`$sort` on All Products and category listings** may be `<attribute_code>` or `-<attribute_code>` when the store has a default sorting attribute and the URL has no `sort`. Direction follows the store setting (ascending unless set to descending). An explicit `sort` query, including `relevance`, is unchanged. No new `$store` key.

## 2026-08-18 — Parent category branch display mode

- **New `$store` key:** `branch_display_mode` (`children` default | `products` | `both`) — store-wide default for how parent categories with children render.
- **Category page view data:** `$branchDisplayMode`, `$showChildren`, `$showProducts`. Themes must branch on these (not `$isLeaf` alone). When products show on a branch, the listing uses descendant-aware `anchor_category_id` filtering.
- **Per-category override:** ProductHub `Category.branch_display_mode` (`null` = inherit store default).
- See `catalog.md` and `view-data.md`.

