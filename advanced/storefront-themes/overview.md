---
title: Storefront Themes
description: Build a custom, server-rendered Blade storefront theme for a B2Bware DataHub store — the full authoring contract.
---

<Info>
This is the authoring contract for **Blade storefront themes** (the server-rendered
storefront). If you are integrating the storefront over HTTP/JSON as an SPA or API consumer,
see [Advanced → Storefront](/advanced/storefront/browse-catalog) instead.
</Info>

A storefront theme is a zip of Blade templates and assets that you upload from the store admin.
The platform validates every upload against a fixed contract (a canonical file surface, a safe
Blade/PHP subset, curated view data, and a design-token system) and re-enforces it at render
time. **You do not need access to the platform source code** — everything you need is on these
pages, and the exact same content ships inside every theme download under `docs/`.

## Start a new theme

<CardGroup cols={2}>
  <Card title="Theme Starter Kit (recommended)" icon="github" href="https://github.com/SyncSpider-GmbH/Theme_B2Bware_Starter_Kit">
    Fork it, use it as a template, or download the ZIP. Ships the reference theme, these docs, and
    bash build/refresh scripts. Working in Cursor is recommended (not required).
  </Card>
  <Card title="Download theme files only" icon="download">
    From the store admin **Themes** page, "Download theme files only" gives you just the upload
    payload (`theme.json`, Blade, assets, `docs/`) to drop into an existing repo or upload directly.
  </Card>
</CardGroup>

## How to read these docs

Always read **[Hard rules](/advanced/storefront-themes/hard-rules)** first, then load the page(s)
for your task. If you use an AI assistant, point it at the bundled `docs/README.md` load matrix
and these pages, and tell it never to invent directives, form types, `$store` keys, or tokens
that aren't listed here.

| Page | Covers |
| --- | --- |
| [Hard rules](/advanced/storefront-themes/hard-rules) | Archive layout, canonical file surface, forbidden Blade/PHP |
| [Blade API](/advanced/storefront-themes/blade-api) | Allowed toolkit, theme directives, helpers |
| [i18n & formatting](/advanced/storefront-themes/i18n-and-formatting) | Translations, locale/currency, dates, numbers |
| [Forms](/advanced/storefront-themes/forms) | The `@storefrontForm` registry |
| [View data](/advanced/storefront-themes/view-data) | Globals, `$store`, feature flags, pricing, variants |
| [AJAX & runtime](/advanced/storefront-themes/ajax-and-runtime) | Sections, events, `window.Storefront` |
| [Catalog](/advanced/storefront-themes/catalog) | Facets, sorting, filters, pagination |
| [SEO & images](/advanced/storefront-themes/seo-and-images) | `@storefrontSeo`, `@storefrontImage` |
| [Server data & auth](/advanced/storefront-themes/fetch-and-auth) | `@fetch`, `@storefrontAuthToken`, API reference |
| [Analytics & slots](/advanced/storefront-themes/analytics-and-slots) | Consent analytics, `@storefrontSlot` |
| [Page recipes](/advanced/storefront-themes/page-recipes) | Per-page view-data contracts |
| [Styling](/advanced/storefront-themes/styling) | Tailwind-first, the head cascade |
| [Design tokens](/advanced/storefront-themes/tokens) | Full token reference, dark mode |
| [Author checklist](/advanced/storefront-themes/checklist) | Override strategy, pre-upload checklist |

## Keeping an old download current

Every bundled `docs/` page carries a link back to its page here. If your download is old, trust
these online pages (or the Starter Kit's `update-theme-docs.sh` refresh script) over the local
copy. Contract changes are recorded in the [changelog](/changelog).
