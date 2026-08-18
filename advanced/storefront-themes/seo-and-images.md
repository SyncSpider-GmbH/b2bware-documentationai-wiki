---
title: SEO & images
description: "@storefrontSeo structured data and @storefrontImage CDN optimisation."
---

<Info>
This page also ships inside the default theme download under `docs/07-seo-images.md`, so offline and AI-assisted authors have the same contract locally. This online version is always the latest.
</Info>

## 9.10 SEO & structured data — `@storefrontSeo`

The platform owns the entire SEO `<head>`. A theme places **`@storefrontSeo` once inside its layout `<head>`** and gets, on every page, for free:

- `<meta name="description">` and `<meta name="robots">`
- `<link rel="canonical">` plus `<link rel="alternate" hreflang>` for every locale (and `x-default`)
- Open Graph (`og:*`) and Twitter Card (`twitter:*`) tags
- JSON-LD structured data: `Organization` + `WebSite` (with a `SearchAction`) on every page, a `BreadcrumbList` matching the on-page trail, and — where relevant — `Product`, `CollectionPage` and `ItemList` graphs.

```blade
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>@yield('title', $store['name'])</title>
    @storefrontSeo
    @yield('head')
    {{-- theme CSS … --}}
</head>
```

**Do not hand-roll SEO tags.** Don't add your own `<meta name="description">`, canonical, hreflang, Open Graph or JSON-LD — `@storefrontSeo` already emits them and a second copy confuses crawlers. The `<title>` stays yours (set it with `@section('title', …)`); everything else in the head is platform-owned. There is no `partials/seo-head.blade.php` — use `@storefrontSeo` instead.

### What each page contributes automatically

| Page                                  | Title / description source                                            | Structured data                     |
| ------------------------------------- | --------------------------------------------------------------------- | ----------------------------------- |
| Product (`product.blade.php`)         | `seo.meta_title` / `seo.meta_description` (→ name / short description) | `Product` (+ price-gated `Offer`)   |
| Category (`category.blade.php`)       | `seo.meta_title` / `seo.meta_description` (→ name / description)       | `CollectionPage` + `ItemList`       |
| Products index (`products.blade.php`) | store defaults                                                        | `ItemList`                          |
| Everything else                       | store defaults                                                        | `Organization` + `WebSite` + `BreadcrumbList` |

Set a page `<title>` from the same SEO data so it matches the meta:

```blade
@section('title', data_get($product, 'seo.meta_title') ?: data_get($product, 'name') ?: t('Product'))
```

### Price visibility

Structured data respects the price-visibility gate (§9.6): when the store hides prices until login, **no** prices appear in any `Offer`, `product:price:*` or `og:availability` tag. You get this automatically — never echo a raw price into a `<meta>` or `<script>` yourself.

### Indexing, robots.txt & sitemap.xml

The tenant's **"Allow search engines to index your pages"** setting is exposed as `$store['indexable']` and drives `<meta name="robots">` automatically; transactional and account pages (cart, checkout, account, login, …) are always `noindex`. The platform also serves a tenant `robots.txt` and `sitemap.xml` — a theme need do nothing for either.

---

## 9.11 Product images — `@storefrontImage`

Catalog and customer media (product photos, gallery images, cart thumbnails) are served from the tenant's Bunny CDN. Wrap **every** product-image `src` with `@storefrontImage(...)` so the CDN delivers a right-sized variant instead of the full-resolution original:

```blade
<img src="@storefrontImage($url, 400, 400, 85)" alt="{{ $product->name }}" loading="lazy">
```

Arguments: `@storefrontImage($url, $width?, $height?, $quality?, $aspectRatio?)`. Width, height and quality are optional integers; aspect ratio is an optional `"16:9"`-style string. Omitted (null) arguments are skipped.

Resolve a product's main image with `resolved_main_media` — the single, ready-to-use image the platform resolves for every product. Cascade (same order as the ProductHub API `main_media` field, so server-rendered themes and the Nexus SPA agree):

1. primary image on **this** product (`is_primary` + `media_type=image`)
2. else this product's first own image by `sort_order`
3. else a child-variant primary (configurable parents with **no** own images)
4. else the first linked category image

Bunny stores the URL under `media_url`:

```blade
@storefrontImage(
    data_get($product, 'resolved_main_media.media_url')
        ?? data_get($product, 'main_media.media_url'),
    400, 400, 85
)
```

> Never read `mainMedia.media_url` directly — `mainMedia` is a has-many relation (a *collection* of primary images), so a dotted `mainMedia.media_url` resolves to `null`. Always use `resolved_main_media` (with `main_media` as the serialized-payload fallback).

On the **product detail** page prefer the controller's `$galleryImages` payload (see *Configurable products*) for the gallery — primary/own-first, then `sort_order`, mode-aware for variants. Pass it to `components/product-gallery` and render the thumbnail rail whenever `count($images) > 1`. Listing cards keep using `resolved_main_media` so the card thumbnail matches the detail main image.

**Gallery rail layout (no custom CSS).** The rail must stay exactly as tall as the main image, however many thumbnails there are. A plain flex sibling can't: its own content height feeds the flex line, so a long rail stretches the row. `components/product-gallery` instead takes the rail out of flow on tablet+ — the figure gets `tablet:relative tablet:pl-24` (only when a rail is rendered) and the rail gets `tablet:absolute tablet:top-0 tablet:bottom-0 tablet:left-0 tablet:w-20`, so the figure's height comes from the main image's `aspect-square` box alone and the rail spans it edge to edge. Inside the rail, the two `h-8` arrows and the `flex-1 min-h-0 overflow-auto` scroll track share that height, so the arrows always sit inside the image's bounds. The arrows are styled as real buttons rather than bare glyphs (`rounded-lg border border-border-subtle bg-neutral-white text-neutral-800`, hover to primary — a border, never a shadow) and take `tablet:w-full` so each one spans the thumbnail column edge to edge; on the phone strip they stay 32px squares. The white fill and `neutral-800` glyph are deliberate literals-via-token so the pair keeps its contrast in dark mode, where the rail sits on a near-black page. The rail is a horizontal strip below the main image on phones (`flex-col-reverse` figure, default `flex-row` rail), where the same two arrow buttons sit **left and right** of the strip: each button ships both glyphs and shows the one matching the current axis (`tablet:hidden` chevron-left/right, `hidden tablet:block` chevron-up/down), and the inline module measures `scrollWidth`/`scrollLeft` below 768px and `scrollHeight`/`scrollTop` above it. Arrow **presence** follows overflow only: once revealed, both arrows stay in the layout and are merely `disabled` + `opacity-40` at the ends. Hiding one at an end (the pattern the header category row uses) would hand its 36px back to the track mid-gesture, and that resize reads as a snap while trackpad-scrolling — the native scroll has to stay fluid, only the arrow clicks animate (`behavior: 'smooth'`).

Recommended sizes per surface (square crops, quality 85):

| Surface                         | Width × Height |
| ------------------------------- | -------------- |
| Catalog grid card               | 400 × 400      |
| Catalog list-row thumbnail      | 200 × 200      |
| Product gallery — main image    | 800 × 800      |
| Product gallery — thumbnail     | 150 × 150      |
| Cart / checkout line thumbnail  | 160 × 160      |
| Order-history line thumbnail    | 80 × 80        |

**Safe to use everywhere.** When the URL is **not** a Bunny CDN URL (a theme `@themeAsset`, the configured placeholder, an external host) or is empty, the helper returns it **unchanged** — so you never need to guard the call. The sizing params only take effect when the **Bunny Optimizer is enabled on the pull zone** (a per-tenant Bunny setting); when it is off the CDN ignores the params and serves the original, so the directive is always harmless. Any existing query string (e.g. a signed token) is preserved.

Keep the placeholder fallback exactly as before — only the real image `src` is wrapped:

```blade
@if(data_get($product, 'resolved_main_media.media_url') ?? data_get($product, 'main_media.media_url'))
    <img src="@storefrontImage(data_get($product, 'resolved_main_media.media_url') ?? data_get($product, 'main_media.media_url'), 400, 400, 85)" alt="{{ $product->name }}" class="w-full h-full object-cover" loading="lazy">
@elseif(!empty($store['product_placeholder']))
    <img src="{{ $store['product_placeholder'] }}" alt="{{ $product->name }}" class="w-full h-full object-cover" loading="lazy">
@else
    <img src="@themeAsset('img/placeholder.svg')" alt="{{ $product->name }}" class="w-full h-full object-contain p-6 opacity-40" loading="lazy">
@endif
```

---
