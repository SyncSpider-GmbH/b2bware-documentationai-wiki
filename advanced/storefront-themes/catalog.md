---
title: Catalog
description: Facets, sorting, price/in-stock filters, view modes, and pagination.
---

## 9.8 Catalog — facets, sorting, price, in-stock, view & pagination

The catalog pages — `products.blade.php` (the All Products index) and `category.blade.php` when `$showProducts` is true — receive a curated set of **layered-navigation** view data. Everything is dynamic and tenant-scoped; the theme never reads ProductHub / AttributesHub directly. Render it with `@foreach` + `data_get`, exactly like every other page.

### Catalog view data

| Variable              | Type            | Meaning                                                                                                 |
| --------------------- | --------------- | ------------------------------------------------------------------------------------------------------- |
| `$products`           | LengthAwarePaginator | The product result set (already filtered / sorted / paginated). Use `->total()`, `->firstItem()`, `->lastItem()`, and iterate for cards. Present only when `$showProducts` is true (otherwise `null`). |
| `$filters`            | array           | `['q' => '<search>']` — the active free-text query (echoed from the header search).                     |
| `$sort`               | string          | The active sort key (see below). Default `'relevance'`.                                                  |
| `$sortOptions`        | array           | **Dynamic** sort entries `['key' => '<attribute_code>'|'-<attribute_code>', 'label' => '<name> ↑/↓']` from attributes flagged `use_for_sorting`. Append them after the five native options. |
| `$view`              | string          | `'grid'` or `'list'` — the active listing layout.                                                       |
| `$facets`             | Collection      | **Contextual** attribute facets: `['id', 'name', 'values' => ['<label>', …]]`. Only values present in the current result set appear (layered navigation); no counts. Empty when the tenant has no filterable attributes. |
| `$categoryFacet`      | Collection      | Category facet rows `['id', 'name', 'slug', 'url', 'count', 'active']`. On the index these are the root categories; on a leaf they are the current category + siblings. `count` is descendant-aware; `url` is ready for `@routeUrl('store.category', ['slug' => …])`. |
| `$selectedAttributes` | array           | Map of `attribute_id => [selected value strings]` — use to mark facet checkboxes `@checked(...)`.       |
| `$priceFilterEnabled` | bool            | Whether to show the price filter (true when prices are visible to the viewer).                          |
| `$priceBounds`        | array/null      | `['min', 'max']` slider bounds from real catalog prices, or `null` (fall back to plain number inputs).  |
| `$priceSelected`      | array           | `['min' => float|null, 'max' => float|null]` — the active price range.                                  |
| `$inStockAvailable`   | bool            | Whether to show the "In stock only" filter (true only when the catalog tracks stock).                   |
| `$inStockSelected`    | bool            | Whether the in-stock filter is active.                                                                  |
| `$pagination`         | array           | `['current_page', 'per_page', 'total', 'last_page']` convenience mirror of the paginator.               |
| `$catalogAttributes`  | array           | **Always present** `[product_id => [{code, name, value, is_url, is_html, is_multiline}, …]]` map of each listed product's visible attributes — for a B2B attribute / spec table. Look up by `(string) $product->id` and pick the columns you want by `code`. Card-grid themes simply ignore it. |

`category.blade.php` additionally receives:

| Variable | Type | Meaning |
| --- | --- | --- |
| `$category` | Category | The resolved category model. |
| `$categorySlug` | string | Full slug path for this page. |
| `$parentSlugPath` | string | Parent path segment (empty at root). |
| `$siblings` | Collection | Navigable siblings (for facets / alternate nav). |
| `$children` | Collection | Direct navigable children. |
| `$isLeaf` | bool | Structural: `true` when `$children` is empty. Do **not** use this alone to decide layout. |
| `$branchDisplayMode` | string | Resolved mode: `children` \| `products` \| `both`. Leafs are always `products`. |
| `$showChildren` | bool | Render the subcategory grid when true. |
| `$showProducts` | bool | Run/render the product listing when true. |

**Branch display mode.** Store default `$store['branch_display_mode']` (tenant `categories.branch_display_mode`, default `children`) plus optional per-category `branch_display_mode` override. Themes must branch on `$showChildren` / `$showProducts` (or `$branchDisplayMode`), not `$isLeaf` alone — otherwise parent categories will never show products even when the merchant enables them. When `$showProducts` is true on a branch, the platform filters with ProductHub `anchor_category_id` (this category **and all descendants**).

### Query parameters (the URL is the state)

Catalog filters are **plain `GET` forms** — never `@storefrontForm` (no route registration, no CSRF; they are idempotent reads). Persist the active state across every control with hidden `<input>`s so changing one dimension keeps the others.

| Param            | Shape                                  | Notes                                                                       |
| ---------------- | -------------------------------------- | --------------------------------------------------------------------------- |
| `q`              | string                                 | Free-text search (set by the header search form).                           |
| `sort`           | `relevance\|newest\|oldest\|name_asc\|name_desc\|<attribute_code>\|-<attribute_code>` | Native keys + any `$sortOptions` key. Unknown keys fall back to natural order. |
| `attr[<id>][]`   | repeated                               | Selected attribute-value labels per filterable attribute id.                |
| `price_min` / `price_max` | number                        | Price range (only honored when `$priceFilterEnabled`).                      |
| `in_stock`       | `1`                                    | In-stock only (only honored when `$inStockAvailable`).                       |
| `view`           | `grid\|list`                           | Listing layout. Submit it as a button `name="view"` so it preserves filters. |
| `page`           | int                                    | Pagination (the windowed `components/pagination` keeps the rest of the query). |

### Product card

`@include('components.product-card', ['product' => $p, 'view' => $view, 'redirect' => '/' . $locale . '/products'])` — pass `view` for the grid/list layout and a **relative** `redirect` so the favorite toggle returns to the current listing (absolute URLs are rejected by `SafeRedirect`). Prices and the add-to-cart CTA defer to the canonical `price` / `add-to-cart-button` components (they already honor `$canSeePrices` / `$canAddToCart`).

> **Custom themes:** the filter sidebar and toolbar are **inlined** into the catalog pages (no new partials — see §2). Replicate the markup per page; do not invent a shared `filters` partial.

---
