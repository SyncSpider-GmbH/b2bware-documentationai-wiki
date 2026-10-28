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
| `$sort`               | string          | The active sort key, and the value to mark selected. When the URL has no `sort`, or sends a key the catalog does not accept, this is the store's default sorting attribute (`<attribute_code>` or `-<attribute_code>`) or `'newest'`. An accepted `sort` query is echoed as-is. Search uses the same key. |
| `$sortOptions`        | array           | **Dynamic** sort entries `['key' => '<attribute_code>'|'-<attribute_code>', 'label' => '<name> ↑/↓']` from attributes flagged `use_for_sorting`. Append them after the native options (newest, oldest, price low to high, price high to low, name A–Z, name Z–A). |
| `$view`              | string          | `'grid'` or `'list'` — the active listing layout.                                                       |
| `$facets`             | Collection      | **Contextual** facets. See **Definition facets** and **Attribute facet display** below. Attribute rows include `code`, `display`, `swatches`, and `counts` (`<label>` => product count). `values` lists only labels that match at least one product in the current context (search, category, the other selected attributes, and — when those filters are active — the price range and "In stock only"). A zero count is omitted. Empty when the tenant has no filterable attributes. |
| `$categoryFacet`      | Collection      | Category facet rows `['id', 'name', 'slug', 'url', 'count', 'active']`. On the index these are the root categories; on a leaf they are the current category + siblings. `count` is descendant-aware; `url` is ready for `@routeUrl('store.category', ['slug' => …])`. |
| `$selectedAttributes` | array           | Map of `attribute_id => [selected value strings]` — use to mark attribute-facet radios or checkboxes `@checked(...)`. Select, radio, and swatch hold one value; multiselect may hold several. |
| `$selectedDefinitions` | array          | Map of `attribute_id => [definition name => [cell, …]]` — use to mark definition-facet checkboxes. Empty when none are selected. |

Facet attributes are product attributes flagged for filtering whose type is `select`, `multiselect`, `radio`, or `swatch`.

Each attribute `$facets` row (`kind=attribute`, or a missing `kind`):

| Key | Meaning |
| --- | --- |
| `id` | Attribute id. Use it in `attr[<id>]`. |
| `code` | `attribute_code`. Stable when the display name or its translation changes. |
| `name` | Translated display name. |
| `multiple` | True only for multiselect. Select, radio, and swatch are single-value. This does not follow `display`. |
| `display` | `null`, or one of `checkbox`, `searchable_select`, `color_swatch`, `boolean_icon`. `null` means checkboxes when `multiple` is true and radios otherwise. The merchant sets this on the attribute; do not choose a control from `name`. |
| `values` | List of translated labels. Each label is the submitted value. |
| `swatches` | Map of label to a safe color (`#rgb`, `#rrggbb`, `#rrggbbaa`, or numeric `rgb()` / `rgba()`). Empty when the option has no usable `swatch_value`. Paint a chip only for `color_swatch`. |
| `counts` | Map of label to how many products that value would leave. A zero count is omitted, and that label is not in `values`. |
| `$priceFilterEnabled` | bool            | Whether to show the price filter (true when prices are visible to the viewer).                          |
| `$priceBounds`        | array/null      | `['min', 'max']` slider bounds from real catalog prices, or `null` (fall back to plain number inputs).  |
| `$priceSelected`      | array           | `['min' => float|null, 'max' => float|null]` — the active price range.                                  |
| `$inStockAvailable`   | bool            | Whether to show the "In stock only" filter (true only when the catalog tracks stock).                   |
| `$inStockSelected`    | bool            | Whether the in-stock filter is active.                                                                  |
| `$activeFilters`      | array           | Applied-filter chips (see below). Empty when nothing is applied, and empty on a category page that is not showing products. |
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

**Branch display mode.** Store default `$store['branch_display_mode']` (tenant `categories.branch_display_mode`, default `children`) plus optional per-category `branch_display_mode` override. Themes must branch on `$showChildren` / `$showProducts` (or `$branchDisplayMode`), not `$isLeaf` alone — otherwise parent categories will never show products even when the merchant enables them. When `$showProducts` is true on a branch, the platform filters with ProductHub `anchor_category_id` (this category **and all descendants**, plus configurable parent products whose variations are assigned to any category in the subtree).

### Query parameters (the URL is the state)

Catalog filters are **plain `GET` forms** — never `@storefrontForm` (no route registration, no CSRF; they are idempotent reads). Persist the active state across every control with hidden `<input>`s so changing one dimension keeps the others.

| Param            | Shape                                  | Notes                                                                       |
| ---------------- | -------------------------------------- | --------------------------------------------------------------------------- |
| `q`              | string                                 | Free-text search (set by the header search form).                           |
| `sort`           | `newest\|oldest\|name_asc\|name_desc\|price_asc\|price_desc\|<attribute_code>\|-<attribute_code>` | Native keys + any `$sortOptions` key. Render `price_asc` and `price_desc` only when `$canSeePrices` is true; a visitor who cannot see prices is not sorted by price. Price order uses the product's regular price. An unknown key is treated as omitted. Omitted `sort` applies the store's default, or `newest` when none is configured. A present, accepted `sort` always wins. |
| `attr[<id>]` / `attr[<id>][]` | scalar or repeated              | Selected attribute-value labels. Select and radio submit one `attr[<id>]` value. Multiselect repeats `attr[<id>][]`. A repeated list on a single-select attribute is collapsed to its first value. Do not use this for a facet whose `kind` is `definition`. |
| `attr_def[<id>][<definition name>][]` | repeated | Selected definition cells. OR within one definition, AND across definitions on the same attribute, OR with `attr` on that attribute, AND across attributes. Unknown names and non-discrete definitions are ignored. Persist them with hidden inputs the same way as `attr`. |
| `price_min` / `price_max` | number                        | Price range (only honored when `$priceFilterEnabled`).                      |
| `in_stock`       | `1`                                    | In-stock only — ProductHub `stock.buyable_qty > 0` (only honored when `$inStockAvailable`). |
| `view`           | `grid\|list`                           | Listing layout. Submit it as a button `name="view"` so it preserves filters. |
| `page`           | int                                    | Pagination (the windowed `components/pagination` keeps the rest of the query). |

The bundled default theme reads `display` on attribute facets and shows `counts` beside each attribute label. Definition facets are always checkboxes named `attr_def[<attribute_id>][<definition name>][]`. It submits either control immediately and debounces price input by 400 ms. The in-stock filter stays `in_stock=1` and uses the same icon chip. Its clear action appears at the top of the filter card and again beside the applied-filter chips. A submit button is rendered only as a no-JavaScript fallback.

A catalog URL whose attribute combination matches nothing stays on that URL and shows an empty grid. The applied-filter chips stay, so the shopper can remove one constraint. The theme does not offer that empty combination as a new radio or checkbox. A theme that only prints `values` already hides those labels; read `counts` to show the number.

### Definition facets

When a filterable attribute has at least one discrete definition (`select`, `multiselect`, `radio`, or `swatch`), the platform does **not** emit that attribute's member labels. It emits one facet per definition:

| Key | Meaning |
| --- | --- |
| `kind` | `definition`. Attribute facets use `attribute` (treat a missing `kind` as `attribute`). |
| `id` | String `"<attribute_id>:<definition name>"`. Not an attribute id — do not put it in `attr[<id>]`. |
| `attribute_id` | The attribute id (int). |
| `definition_name` | Stored definition name. Use it in the input name and in `$selectedDefinitions`. |
| `definition_type` | `select`, `multiselect`, `radio`, or `swatch`. |
| `name` | Same as `definition_name` (the sidebar heading). |
| `multiple` | Always `true`. |
| `values` | Definition cells present on products in the current result set. |

Checked state is `$selectedDefinitions[$facet['attribute_id']][$facet['definition_name']]`. A theme that still submits `attr[<facet id>]` for these rows sends the cell as a member label and the filter misses.

### Attribute facet display

| `display` | Control |
| --- | --- |
| `null` | Checkboxes when `multiple` is true, otherwise radios. |
| `checkbox` | Checkboxes. A single-value attribute still posts one `attr[<id>]` value. |
| `searchable_select` | The same radios or checkboxes, with a search box that only hides options in the browser. The box has no `name`, so it is not submitted. |
| `color_swatch` | The same radios or checkboxes, plus a color chip from `swatches`. A missing color is a neutral chip and the label. |
| `boolean_icon` | One generic icon chip per value. The underlying radio or checkbox still submits the label. A custom theme can pick a different glyph from `code` and the value. |

### Applied filters (`$activeFilters`)

Each entry is one applied constraint and a URL that reloads the same listing without it:

| Key | Meaning |
| --- | --- |
| `kind` | `attribute`, `definition`, `price_min`, `price_max`, `in_stock`, or `search`. |
| `name` | Attribute name for `attribute` chips, definition name for `definition` chips, otherwise `null`. |
| `value` | The selected label, formatted price, or search text. `null` for `in_stock`. |
| `url` | Same catalog route with that one constraint removed. |

There is one `attribute` chip per selected value, so removing "Color: Red" keeps "Color: Blue". There is one `definition` chip per selected cell, so removing "Farbgruppe: blau" keeps "Farbgruppe: rot" and any other definition. Min and max price are separate chips. Search (`q`) is a chip because clearing filters already drops it. Sort, view, the current category, and pagination are not chips.

A chip URL drops `page`. It keeps `sort` only when the request already had `sort`, keeps `view` when it is not `grid`, keeps `per_page` when the request set it, and keeps every other applied filter. Price values are the normalized range (a reversed min/max pair is already swapped).

The default theme renders these chips above the product grid via `partials/catalog-active-filters.blade.php` on All Products and on category pages that show products. The **Clear filters** link next to them drops every filter and keeps a non-grid `view`, matching the link in the filter card.

### Product card

`@include('components.product-card', ['product' => $p, 'view' => $view, 'redirect' => '/' . $locale . '/products'])` — pass `view` for the grid/list layout and a **relative** `redirect` so the favorite toggle returns to the current listing (absolute URLs are rejected by `SafeRedirect`). Prices and the add-to-cart CTA defer to the canonical `price` / `add-to-cart-button` components (they already honor `$canSeePrices` / `$canAddToCart`).

> **Custom themes:** the filter sidebar and toolbar are **inlined** into the catalog pages (no new partials — see §2). Replicate the markup per page; do not invent a shared `filters` partial.

---
