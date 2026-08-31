---
title: Pricing
description: The pricing rendering contract — how prices resolve and exactly how each surface displays them.
---

## 9.16 Pricing — the rendering contract

This page is the **single source of truth** for how prices are resolved and rendered on the
storefront. Every surface (catalog card, product detail, cart line) derives from the same
resolution, and the platform's matrix tests assert the table below row by row — if you change
pricing display behaviour, change this page, the resolver and the tests together.

**A theme never sets, computes, or fetches a price.** Every figure is computed server-side
and handed to Blade as ready view data (`$priceViews` / `$priceView` / `$cartLines` /
`$tierPrices` / `$contractPrice`). Render those; never multiply, discount, or tax-adjust in Blade.

## What affects a price

| Input | Where it lives | Effect |
| --- | --- | --- |
| Regular ("list") price | product `price` | The struck-through baseline everywhere. |
| Special price (date-windowed) | product `specialPrice` | Candidate for the current price. |
| Group / company-group price | resolved into `finalPrice` | Candidate for the current price. |
| Tier price with min qty 0/1 | resolved into `finalPrice` | The customer's **base** price — *not* a volume discount. |
| Tier prices with min qty > 1 | `$tierPrices` (product page) | Quantity-dependent unit price; also what the cart charges at that qty. |
| Catalog price rules | RuleHub | Stacked **on top of** whichever base wins. |
| ERP / provider price | pricing addon | Supersedes the whole DB cascade; rules still stack. |
| Tax display mode | `$store['display_prices_with_tax']` | Net/gross split pre-computed server-side (`has_tax` gates VAT labels). |
| Price visibility | `$canSeePrices` | Guests may get "Log in to see prices" instead. |
| Zero-price policy | `$store['zero_price_as_quote']` | Zero/absent price renders "Request quote". |

## The resolution (server-side, identical on every surface)

```
current  = ERP provider price            (catalog rules stacked on top)
         → finalPrice                    (tier 0/1 → group → valid special → regular,
                                          catalog rules stacked on top)

compare  = regular list price, whenever list > current
           — regardless of WHICH mechanism produced the discount

priceView = { current_excl, current_incl, compare_excl, compare_incl, has_tax }
```

**Invariant:** the displayed price is always the figure the cart will charge at quantity 1;
the struck price is always the regular list price.

## The rendering matrix

`~~x~~` = struck through. Each row is asserted by a platform matrix test carrying the same
`UC` number.

| UC | Scenario | Catalog card | Product detail | Cart line |
| --- | --- | --- | --- | --- |
| 1 | Regular price only | current | current | line total (+ "*x* each" when qty > 1) |
| 2 | Guest + login-gated prices | "Log in to see prices" | same; no add-to-cart | n/a |
| 3 | Valid special price < list | ~~list~~ current | ~~list~~ current | ~~list × qty~~ total |
| 4 | Group / company-group / contract price | ~~list~~ current | ~~list~~ current + "Your contracted price" badge | ~~list × qty~~ total |
| 5 | Only a 1+ tier (equals the contract price) | ~~list~~ current | **one** price render: ~~list~~ current + badge; **no Volume section** | ~~list × qty~~ total |
| 6 | Multi-tier 1+ / 10+ / 50+ (1+ = current) | ~~list~~ current; live total tier-aware (UC 14) | as UC 4 + Volume cards for 10+ / 50+ **only** | qty 10 → tier unit charged; ~~list × qty~~ total |
| 7 | Catalog price rule | ~~list~~ current | same | ~~list × qty~~ total + rule name |
| 8 | ERP provider price < list | ~~list~~ provider price | same + badge | same |
| 9 | Zero price + `zero_price_as_quote` | "Request quote" | "Request quote" | — |
| 10 | Tax mode `including_tax` / `both` | pre-computed net/gross splits; VAT label only when `has_tax` | same | same |
| 11 | Cart: quantity matches a tier | — | — | unit = tier price; ~~list × qty~~ shown |
| 12 | Cart: catalog-rule line | — | — | ~~list × qty~~ + rule names |
| 13 | Configurable parent without own price | price hidden | bulk variant table owns purchase | — |
| 14 | List view, quantity stepper changed | live total = matched tier unit × qty; ~~list × qty~~ appears when discounted | — | — |

Edge rules the platform enforces:

- **Badge** (`$contractPrice`): authenticated customer AND display price strictly < list.
  The badge is a **label only** — never repeat figures inside it; the main price block owns
  both figures.
- **Volume cards** (`$tierPrices`): only tiers whose price **differs** from the displayed
  unit price arrive in view data (a 1+ tier *is* the base price, not an extra discount).
  Render the section only when the collection is non-empty.
- **Strike**: shown only when list > current — never strike an equal price.

## Per-surface rendering rules (default theme)

### Catalog card (products / category / favorites)

- Unit price via `components/price` with `data_get($priceViews, (string) $product->id)` —
  `price__compare` (struck) + `price__current` render from the view-model, nothing else.
- List view emits `data-line-unit`, `data-line-original-unit` and `data-tier-prices` (JSON,
  min > 1 tiers) on the row; the page script updates `[data-line-total]` and toggles the
  struck `[data-line-original]` as the quantity changes. Progressive enhancement only — the
  cart recomputes server-side on add.

### Product detail

- **One** price render: `components/product-price` (struck list + current, size `lg`)
  plus the `product__contract-badge` pill when `$contractPrice` is set.
- Volume discount section: iterate `$tierPrices` as `product__tier-card`s; the platform has
  already filtered out tiers equal to the displayed price — do not re-add a 1+ card.
- Variant rows carry their own `priceView` per row — render via `components/price`.

### Cart line items

- Line total via `components/price` from the line's `line_total_excl` / `line_total_incl`.
- When `$line['has_discount']`, show `cart__item-was` — the struck original
  (`original_price_excl|incl` × qty, list-price baseline) — plus any
  `applied_catalog_rules` names (`cart__item-rule`).
- Otherwise, with qty > 1 show the per-unit "each" hint (`cart__item-each`).

## Do / don't

1. ✅ Render prices exclusively from the pricing view data (ideally via `components/price`).
2. ✅ Keep the strike + current pair together — one price block per surface.
3. ❌ Never compute a discount, stack a rule, or compare prices in Blade.
4. ❌ Never render the same figure twice on one surface (box + price + tier card).
5. ❌ Never tax-qualify a price the view-model didn't mark `has_tax`.
