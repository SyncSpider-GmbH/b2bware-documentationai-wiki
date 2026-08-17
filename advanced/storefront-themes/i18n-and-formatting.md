---
title: Internationalisation & formatting
description: Translations, active locale/currency, and locale-aware date/number formatting.
---

<Info>
This page also ships inside the default theme download under `docs/02-i18n-format.md`, so offline and AI-assisted authors have the same contract locally. This online version is always the latest.
</Info>

## 9.1 Translations

The storefront supports **two complementary strategies** for translating a page. Most themes only ever need the first one; reach for the second only when an entire page diverges significantly across locales.

### Strategy A — `@t()` inside a single template (recommended default)

Wrap every user-facing English string in `@t(...)` (in HTML body) or `t(...)` (inside an expression like a section argument or `@include` array). The platform looks each English source string up in the Settings Hub `Translations` table for the active URL locale and returns the translated value, or falls back to the source string when no translation exists.

```blade
@extends('layouts.shop')

@section('title', t('Shop'))

@section('content')
    <h1>@t('Shop')</h1>
    <p>@t('Welcome back, please choose a product below.')</p>

    @include('components.empty-state', [
        'title'   => t('No products yet'),
        'message' => t('Check back soon.'),
    ])
@endsection
```

**Authoring conventions for translation keys**:

- The argument **is** the English source string. There are no abstract keys like `shop.title` — readability of the blade file is the first priority.
- Capitalize naturally (`'No products yet'`, not `'no products yet'`). The translator copies the casing.
- Punctuation belongs **inside** the call: `@t('Welcome!')`, `@t('Sort by')` (note no trailing colon — add the colon outside if it should not be translated).
- Single quotes for the call; if the string contains an apostrophe, use double quotes (`@t("What\’s new")`).
- Strings without a translation in the active locale render as the English source. **No errors, no fallbacks to write** — ship a partial dictionary if you want.
- Translations are cached per installation + locale. Editing a translation in Settings Hub invalidates the cache automatically.

#### Injecting values into a translated string

Pass extra arguments to `@t` / `t()` and they are injected with **printf** semantics *after* the translation lookup. The English source string carries the specifiers and stays the translation key, so every locale keeps them in whatever position that language needs:

```blade
{{-- key:    "Up to %d rows per file."                      --}}
{{-- de-de:  "Bis zu %d Zeilen pro Datei."                  --}}
@t('Up to %d rows per file.', $maxRows)

{{-- Two values are filled left to right. --}}
@t('Your file has %d rows and the limit is %d.', $rows, $maxRows)

{{-- Works the same in expression position. --}}
@include('components.empty-state', ['title' => t('No results for “%s”', $query)])
```

- Use the standard specifiers — `%d` (integer), `%s` (string), `%.2f` (fixed decimals). Escape a literal percent as `%%` **only in strings that take arguments**; a string with no arguments is never formatted, so a lone `%` in it is safe.
- **Never** use this for money, numbers or dates — `@formatCurrency`, `@formatNumber` and `@formatDate` are locale-aware and `%d`/`%s` are not (see §9.3, §9.4).
- Values are still escaped by the directive, so a user-supplied value is safe to inject.
- If a translation loses or reorders a specifier, the platform falls back to the English source rather than erroring — a broken translation can never take the page down.

### Strategy B — per-locale page overrides (when an entire page is structurally different)

When a single locale needs a substantially different layout — different sections, different copy density, locale-specific marketing blocks — ship an alternate page template under a locale folder. The storefront resolves pages in this order:

1. `pages/{locale}/<name>.blade.php` in the **active theme**
2. `pages/<name>.blade.php` in the **active theme**
3. `pages/{locale}/<name>.blade.php` in the **default theme**
4. `pages/<name>.blade.php` in the **default theme**

The `{locale}` segment is the lowercased BCP-47 tag from the URL (`en`, `de-de`, `pt-br`).

```
pages/login.blade.php           # base English template (uses @t for everything else)
pages/de-de/login.blade.php     # bespoke German login page — pure German strings, no @t needed
pages/de-de/about-us.blade.php  # German-only custom page
```

Account sub-pages may be overridden the same way:

```
pages/de-de/account/orders.blade.php
```

**Rules for locale folders**:

- The folder name must be a lowercased BCP-47 tag: `[a-z]{2,3}` plus zero or more `-[a-z0-9]{2,8}` segments. Examples: `en`, `de`, `de-de`, `pt-br`, `zh-hant-tw`. Uppercase forms like `de-DE` are rejected.
- Inside the locale folder you may ship any canonical page (`login.blade.php`, `account/orders.blade.php`, …) **or** any custom page slug, with the same filename rules as the root `pages/` folder.
- A per-locale page is a **complete replacement**, not a partial — it does not inherit content from `pages/<name>.blade.php`. It still inherits from its `@extends('layouts.shop')` layout normally.
- Inside a per-locale page you are free to write pure target-language strings (`<h1>Anmelden</h1>`) and skip `@t(...)`. You may still use `@t()` if you want — it works the same way.
- Locale overrides apply to **pages only**. Layouts, partials, and components are shared across locales — translate their strings with `@t(...)`.

### Which strategy should I pick?

| Situation                                                                  | Use            |
| -------------------------------------------------------------------------- | -------------- |
| Translating labels, headings, button text, validation copy                 | `@t()` (A)     |
| Marketing landing pages, hero copy, country-specific legal pages           | per-locale (B) |
| One or two locales differ visually from the rest                           | per-locale (B) |
| You want translators to work from a dictionary in Settings Hub             | `@t()` (A)     |
| You want the page maintained by a copywriter who doesn't know Blade syntax | per-locale (B) |

The two strategies coexist: a theme can have `pages/checkout.blade.php` using `@t()` for 30 languages, and `pages/de-de/checkout.blade.php` for a bespoke German checkout.

---

## 9.2 Reading the active locale and currency

The URL is the **single source of truth** for the active locale at request time. The `{locale}` segment in the path (`/de-de/products`) is the only thing that decides what the page renders in — any syntactically valid BCP-47 tag is accepted, the middleware does **not** allow-list against the SettingsHub-configured locale list. The configured locales (`global_config.i18n.locales[]`) are used purely as the menu for the switcher UI; the configured default (`global_config.i18n.locale.locale`) is consulted only when a visitor hits `/` and we need a target for the redirect.

A `storefront_locale` cookie (set by the switcher via `POST /locale`) overrides the configured default on `/` landings. The cookie is never used to override the URL — if the URL says `/en-us`, the page is `en-us`, even if the cookie says `de-de`.

The active locale and currency are exposed to every theme template through three places:

- `$locale` view variable (injected globally by the platform) — the lowercased BCP-47 tag from the URL, e.g. `de-de`.
- `@routeUrl('store.products')` — automatically prefixes the active locale segment when the route declares `{locale}`. Pass a third argument (`@routeUrl('store.products', [], $otherLocale)`) to build the URL for a specific language.
- `localeUrl($otherLocale)` — returns the **current** page URL in `$otherLocale`, used by locale switchers.

### Switcher contract

A locale switcher MUST:

1. Render only the platform-provided locales. Use **`$localeOptions`** — the rich rows the platform injects (see §9.6 globals). Each row is `['code', 'label', 'short', 'flag', 'url', 'active']`, so you get the display label, the switch URL and the active flag without recomputing anything. (`$availableLocales` is the low-level `string[]` of tags; prefer `$localeOptions` for UI.)
2. On change, `POST /locale` (route name `store.locale.set`) with `{ "locale": "<bcp47>" }` to persist the visitor's choice as a cookie.
3. Full-page navigate to the row's `url` (equivalently `localeUrl($code)`) so the next request's URL drives the locale.

Inline the switcher's JS in the same blade as the markup (see [`partials/locale-switcher.blade.php`](partials/locale-switcher.blade.php) for the reference implementation).

```blade
{{-- Locale switcher — drive it from $localeOptions --}}
<ul>
    @foreach($localeOptions ?? [] as $option)
        <li>
            <a href="{{ $option['url'] }}" @if($option['active']) aria-current="true" @endif>
                {{ $option['label'] }}
            </a>
        </li>
    @endforeach
</ul>

{{-- hreflang tags in <head> --}}
@foreach($localeOptions ?? [] as $option)
    <link rel="alternate" hreflang="{{ $option['code'] }}" href="{{ $option['url'] }}">
@endforeach
```

---

## 9.3 Date formatting

Use `@formatDate(...)` (or the `formatDate(...)` helper inside expressions) for **every** date or datetime rendered in a theme. Never echo `{{ $order->created_at }}` directly — you'll leak a server-locale Carbon string.

```blade
{{ formatDate($order->created_at) }}            {{-- locale-default short date --}}
{{ formatDate($order->created_at, 'LL') }}      {{-- locale long date --}}
{{ formatDate($order->created_at, 'YYYY-MM-DD') }}  {{-- explicit ISO date --}}
```

### Signature

```
formatDate(mixed $value, ?string $format = null): string
```

- `$value` accepts a Carbon instance, a `DateTimeInterface`, or any string Carbon can parse (`'2026-06-04T10:00:00Z'`, `'2026-06-04'`).
- `$format` is an **`isoFormat` token string** (the moment.js / day.js syntax), not PHP `date()` syntax. When omitted, the platform uses `'L'` — the locale-default short date.

This matches what Shopify Liquid, Shopware 6, and Magento 2 do: a small set of locale-aware presets (`L`, `LL`, `LLL`, `LLLL`, `LT`, `LTS`) plus the option to override with an explicit token string when you need a fixed format like an ISO date.

### Locale-aware presets (recommended)

| Token     | Description                            | Example (`en`)         | Example (`de`)            |
| --------- | -------------------------------------- | ---------------------- | ------------------------- |
| `L`       | Short date                             | `06/04/2026`           | `04.06.2026`              |
| `LL`      | Long date                              | `June 4, 2026`         | `4. Juni 2026`            |
| `LLL`     | Long date + short time                 | `June 4, 2026 9:30 AM` | `4. Juni 2026 09:30`      |
| `LLLL`    | Day of week + long date + time         | `Thursday, June 4, 2026 9:30 AM` | `Donnerstag, 4. Juni 2026 09:30` |
| `LT`      | Short time                             | `9:30 AM`              | `09:30`                   |
| `LTS`     | Short time with seconds                | `9:30:25 AM`           | `09:30:25`                |

Use a locale-aware preset whenever the date is part of UI copy — order date, comment timestamp, blog post date, etc. Locale presets respect the active URL locale automatically.

### Explicit format tokens (for fixed presentations)

Reach for explicit tokens only when the date **must** look the same in every locale (invoices, machine-readable timestamps, technical IDs).

| Token       | Output                |
| ----------- | --------------------- |
| `YYYY`      | `2026`                |
| `MM` / `M`  | `06` / `6`            |
| `MMM`       | `Jun` (localized)     |
| `MMMM`      | `June` (localized)    |
| `DD` / `D`  | `04` / `4`            |
| `dddd`      | `Thursday` (localized)|
| `HH` / `H`  | `09` / `9`  (24h)     |
| `hh` / `h`  | `09` / `9`  (12h)     |
| `mm`        | `30`                  |
| `ss`        | `25`                  |
| `A` / `a`   | `AM` / `am`           |

Full token list: see [day.js / moment.js `format`](https://day.js.org/docs/en/display/format).

```blade
{{ formatDate($order->created_at, 'YYYY-MM-DD') }}      {{-- 2026-06-04 --}}
{{ formatDate($invoice->issued_at, 'LL') }}             {{-- June 4, 2026 --}}
<time datetime="{{ formatDate($post->published_at, 'YYYY-MM-DDTHH:mm:ssZ') }}">
    {{ formatDate($post->published_at, 'LL') }}
</time>
```

---

## 9.4 Number & currency formatting

Use `@formatCurrency(...)` for **every** monetary value (prices, totals, discounts, refunds) and `@formatNumber(...)` for plain numeric values (counts, weights, ratings, stock levels). Never write `{{ number_format($price, 2) }}` or `{{ $price . ' ' . $currency }}` — both ignore the active locale.

```blade
{{ formatCurrency($product->price) }}           {{-- $19.99 / 19,99 € / 19,99 kn  --}}
{{ formatCurrency($product->price, 'EUR') }}    {{-- force EUR regardless of active currency --}}

{{ formatNumber($product->stock) }}             {{-- 1,234 / 1.234 (locale-grouped) --}}
{{ formatNumber($product->weight, 3) }}         {{-- 2.500 (3 fraction digits) --}}
```

### Signatures

```
formatCurrency(float|int|string $value, ?string $currency = null): string
formatNumber  (float|int|string $value, int $maxFractionDigits = 2): string
```

- Both honour the active URL locale: number-grouping (`1,234.56` vs `1.234,56`), currency symbol position, narrow vs full symbol, and digit shape are picked by ICU's `NumberFormatter`.
- `$currency` is an ISO 4217 code (`'USD'`, `'EUR'`, `'HRK'`). When omitted, the platform reads `storefronthub.currency` from settings, falling back to the platform default.
- The currency symbol is rendered automatically — do **not** prefix or suffix a manual `€` / `$` / `kn` in markup.

### Examples by locale

| Active locale | `formatCurrency(1234.5)` (USD) | `formatNumber(1234.5)` |
| ------------- | ------------------------------ | ---------------------- |
| `en-us`       | `$1,234.50`                    | `1,234.5`              |
| `en-gb`       | `US$1,234.50`                  | `1,234.5`              |
| `de-de`       | `1.234,50 $`                   | `1.234,5`              |
| `fr-fr`       | `1 234,50 $US`                 | `1 234,5`              |
| `ja-jp`       | `US$1,234.50`                  | `1,234.5`              |

This follows the same approach as Shopify (`{{ price | money }}`), Shopware (`{{ price|currency }}`), and Magento (`<?= $block->formatCurrency(...) ?>`) — one helper that picks symbol and formatting from the storefront locale + a configured currency.

### When to pass an explicit currency

- **Multi-currency cart line item** showing the original currency next to the converted price.
- **Invoice** that is legally required to display the transaction currency, not the active currency.
- **Price comparison widget** showing the same product in multiple currencies.

In the common case (storefront with a single configured currency), let the helper resolve it.

### Common pitfalls

- `formatNumber($x, 0)` rounds to a whole number — it does **not** strip trailing zeros from a fractional value silently.
- `formatCurrency` always renders the configured currency symbol; if you need just the digits (e.g. price-input prefill), use `formatNumber` and add the symbol next to the input chrome.
- These helpers are **display-only** — keep raw `float`/`int` values for math, never re-parse a formatted string.

---
