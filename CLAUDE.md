# B2Bware DataHub API — Claude Code Reference

## Platform Overview

B2Bware DataHub is a modular commerce API platform organized into specialized **Hubs** (and a few product modules). Each hub manages a distinct domain while sharing consistent patterns for authentication, filtering, pagination, and response formats.

See the full hub index: [Hub Overview](/hubs/overview) and [Hub Settings](/core-concepts/hub-settings). Per-hub OpenAPI specs live under [API Reference](/api-reference).

## Architecture

All endpoints follow this URL pattern:
```
https://api.datahub.syncspider.com/api/v1/apps/{hub-slug}/{resource}
```

The default API domain is `api.datahub.syncspider.com`.

### Core commerce hubs

| Hub | Slug | Description |
|-----|------|-------------|
| ProductHub | `product-hub` | Products, categories, pricing, stock, media, variations |
| OrderHub | `order-hub` | Orders, carts, checkout, quotes, payment methods |
| CustomerHub | `customer-hub` | Customers, companies, addresses, roles, groups |
| AttributesHub | `attributes-hub` | Dynamic attributes, types, values, groups |
| MediaHub | `media-hub` | Media management with CDN proxy |
| NotificationHub | `notification-hub` | Multi-channel notifications |
| TaxHub | `tax-hub` | Tax calculation, rules, jurisdictions |
| SettingsHub | `settings-hub` | Platform configuration, locales, currencies |
| LicenseHub | `license-hub` | License key lifecycle |
| AuthHub | `auth-hub` | Login, register, password reset, impersonation |
| EventHub | `event-hub` | Webhook subscriptions and delivery logs |
| RuleHub | `rule-hub` | Promotions, coupons, shipping-rate rules |
| AutomationHub | `automation-hub` | Flow automation |
| DashboardHub | `dashboard-hub` | Dashboard layouts and widgets |
| IntegrationHub | `integration-hub` | Connectors, sync, file feeds, embed |
| StorefrontHub | `storefront-hub` | Themes, custom domains, tenant storefront flags |
| StorefrontBuilderHub | `storefront-builder-hub` | Visual pages and documents |
| InvoiceHub | `invoice-hub` | Invoices, credit notes, dunning |
| LoyaltyHub | `loyalty-hub` | Programs, wallets, rewards |
| AiHub | `ai-hub` | AI provider + assistants |
| PunchOutHub | `punch-out-hub` | OCI/cXML punchout |
| AccountingHub | `accounting-hub` | Bank accounts, reconciliation |
| ProcurementHub | `procurement-hub` | Suppliers, POs, bills |

Modules (same URL pattern): `customer-sku-module`, `customer-product-permission-module`, `customer-category-permission-module`, `transactions-module`, `stock-movements-module`, `dtone-hub`, `a1-top-up-module`, `mesonic-dataflow-real-time-pricing`.

## Authentication

All endpoints require Bearer token auth (except documented public endpoints):

```
Authorization: Bearer {api_token}
Accept: application/json
Content-Type: application/json  # for POST/PUT/PATCH
```

## Pagination

List endpoints use:

```
?page=1&per_page=25
```

Flat response shape:

```json
{
  "data": [...],
  "current_page": 1,
  "total_pages": 10,
  "per_page": 25,
  "total": 250
}
```

Do **not** use `last_page` or wrapped `meta.pagination`.

## Filtering

See [Filtering](/core-concepts/filtering) — CommonFilterRepository JSON filter arrays on `filter[field]`.

## Hub settings

Installation-scoped App Settings: [Hub Settings](/core-concepts/hub-settings).
