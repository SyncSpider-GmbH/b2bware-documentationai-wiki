---
title: Theme README and CHANGELOG
description: The README.md every theme must ship and the optional CHANGELOG.md, both shown to the shop owner in the store admin.
---

## Why

A theme is usually written by an AI assistant or a developer, but it is chosen, previewed and
activated by the shop owner. The store admin shows the theme's `README.md` and `CHANGELOG.md` on
the theme's page, so the owner can see what a theme does and what changed before activating a
version. Write both **for the shop owner**: plain language, no code, no file paths unless they
help name a page.

## README.md (required)

`README.md` sits at the theme root next to `theme.json`. An upload is **rejected** at the manifest
step when:

- `README.md` is missing or empty (the file name must be `README.md` or `readme.md`),
- it is larger than 64 KB or not UTF-8 text,
- any of the four required `## ` sections below is missing or has no text under it.

HTML comments (`<!-- … -->`) do not count as text, so the template below is rejected until it is
filled in. Keep the heading text exactly as written; extra sections (for example a developer
section at the end) are allowed.

| Section | What to write |
| --- | --- |
| `## Purpose` | One or two sentences: who the theme is for and what it should achieve. |
| `## What this theme changes` | One bullet per visible change, grouped by area (header, product page, cart sidebar, colors and fonts, …). Say what the shopper sees. |
| `## Scripts and libraries` | Every script, font or library the theme adds and why. Write `None.` when there are none. |
| `## Still on the default theme` | Pages and sections the theme does not touch — they keep receiving default-theme updates. |

Template (also shipped as `README.md` in the starter kit and in any download that has none):

```markdown
# Theme name

## Purpose

<!-- One or two sentences: who the theme is for and what it should achieve. -->

## What this theme changes

<!-- One bullet per visible change, grouped by area. -->

## Scripts and libraries

<!-- Every script, font or library the theme adds and why, or "None." -->

## Still on the default theme

<!-- Pages and sections the theme does not touch. -->
```

Example of a filled-in `## What this theme changes`:

```markdown
## What this theme changes

- Header: logo on the left, larger search field, announcement bar with the delivery cut-off time.
- Product page: bigger gallery, price and "Add to cart" moved above the description.
- Cart page (`cart.sidebar`): free-delivery note under the totals; the rest of the cart is default.
- Colors and fonts: brand blue buttons and links, Inter for all text.
```

## CHANGELOG.md (optional, recommended)

`CHANGELOG.md` sits at the theme root too. It is not required, but when present the same limits
apply (64 KB, UTF-8) and a file that breaks them rejects the upload. Add one entry at the top for
every upload, newest first, in the same plain language:

```markdown
# Changelog

## v3 — 2026-10-11

- Product page: delivery time shown next to the stock status.
- Cart: removed the promo banner.

## v2 — 2026-09-30

- Header: new announcement bar.
```

## Keep them current

Update both files in the same change as the theme files they describe. When an AI assistant
edits the theme, have it update `README.md` (what the theme changes now) and add a
`CHANGELOG.md` entry before zipping.
