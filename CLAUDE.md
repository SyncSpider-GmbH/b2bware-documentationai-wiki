# B2Bware DataHub API — Claude Code Reference

## Platform Overview

B2Bware DataHub is a modular commerce API platform organized into 9 specialized **Hubs**. Each hub manages a distinct domain while sharing consistent patterns for authentication, filtering, pagination, and response formats.

## Architecture

All endpoints follow this URL pattern:
```
https://api.datahub.syncspider.com/api/v1/apps/{hub-slug}/{resource}
```

The default API domain is `api.datahub.syncspider.com`. This works for all DataHub instances.

### Hub Slugs

| Hub | Slug | Description |
|-----|------|-------------|
| ProductHub | `product-hub` | Products, categories, pricing, stock, media, variations, vendors |
| OrderHub | `order-hub` | Orders, carts, checkout, quotes, payment methods |
| CustomerHub | `customer-hub` | Customers, companies, addresses, roles, groups |
| AttributesHub | `attributes-hub` | Dynamic attributes, types, values, groups |
| MediaHub | `media-hub` | Media management with CDN proxy (Bunny CDN) |
| NotificationHub | `notification-hub` | Multi-channel notifications (120+ endpoints) |
| TaxHub | `tax-hub` | Tax calculation, rules, jurisdictions |
| SettingsHub | `settings-hub` | Platform configuration, locales, currencies, cache |
| LicenseHub | `license-hub` | License key lifecycle management |

## Authentication

All endpoints require Bearer token auth (except public CDN and webhook endpoints):

```
Authorization: Bearer {api_token}
Accept: application/json
Content-Type: application/json  # for POST/PUT/PATCH
```

### Public Endpoints (no auth required)
- `GET /api/v1/apps/media-hub/cdn/{domain}/{path}` — CDN proxy
- `GET /api/v1/apps/order-hub/payment/webhook/{installationKey}/{provider}` — Payment webhook
- `GET /api/v1/apps/order-hub/order/payment/{installationKey}/{order_id}` — Payment redirect

## Pagination

All list endpoints return paginated responses:

```
?page=1&per_page=25
```

Response structure:
```json
{
  "data": [...],
  "current_page": 1,
  "last_page": 10,
  "per_page": 25,
  "total": 250,
  "from": 1,
  "to": 25
}
```

## Sorting

Use `sort` parameter. Prefix with `-` for descending:
```
?sort=-_created_at,name
```

## Filtering

MongoDB-compatible filtering via `CommonFilterRepository`:

```
?filter[field_name]=[{"condition":"operator","value":"value"}]
```

### Operators

| Operator | Example |
|----------|---------|
| `=` | `[{"condition":"=","value":"active"}]` |
| `!=` | `[{"condition":"!=","value":"deleted"}]` |
| `>`, `<`, `>=`, `<=` | `[{"condition":">=","value":100}]` |
| `LIKE` | `[{"condition":"LIKE","value":"%search%"}]` |
| `IN` | `[{"condition":"IN","value":["active","pending"]}]` |
| `NOT IN` | `[{"condition":"NOT IN","value":["canceled"]}]` |
| `EMPTY` | `[{"condition":"EMPTY"}]` |
| `NOT EMPTY` | `[{"condition":"NOT EMPTY"}]` |

### Combining Conditions

AND (range): `?filter[price]=[{"condition":">=","value":100},{"condition":"<=","value":500,"operator":"AND"}]`

OR: `?filter[status]=[{"condition":"=","value":"active"},{"condition":"=","value":"pending","operator":"OR"}]`

### Relation Filters (dot notation)

```
?filter[company.name]=[{"condition":"LIKE","value":"%Acme%"}]
```

### Callback/Search Filters (simple key=value)

```
?filter[search]=term
```

### ProductHub Attribute Filter (special)

```
filter[attribute]=[{"attribute_id":1,"attribute_value":"Red,Blue","condition":"IN","operator":"AND"}]
```

Conditions: `IN`, `NOT_IN`, `EQUALS`, `NOT_EQUALS`, `LIKE`, `GT`, `LT`, `GTE`, `LTE`

## Includes (Eager Loading)

Load related resources with `include` parameter, comma-separated, dot notation for nesting:

```
?include=price,finalPrice,mainMedia,categories.category
```

**Performance**: Only include what you need. Avoid 3+ nesting levels on large lists.

## Error Handling

| Code | Meaning |
|------|---------|
| `200` | OK |
| `201` | Created |
| `204` | No Content (DELETE) |
| `400` | Bad Request (malformed JSON/params) |
| `401` | Unauthorized (missing/invalid token) |
| `403` | Forbidden (insufficient permissions) |
| `404` | Not Found |
| `422` | Validation Error |
| `500` | Server Error |

Validation error format:
```json
{
  "message": "The given data was invalid.",
  "errors": {
    "field_name": ["Error description."]
  }
}
```

---

## ProductHub — `api/v1/apps/product-hub/`

The most complex hub. Manages products, categories, pricing, stock, media, variations, vendors, translations.

### Endpoints

**Products**: `GET/POST /products`, `GET/PUT/DELETE /products/{id}`
- `PUT /products/upsert/single` — Upsert by SKU (idempotent, for ERP sync)
- `PUT /products/bulk/update` — Bulk update
- `DELETE /products/bulk/delete` — Bulk delete
- `PUT /products/{id}/createVariations` — Generate child variations
- `PUT /products/{id}/attachVariationsAttributes` — Attach variation attributes
- `DELETE /products/{parentId}/child-products` — Remove children
- `PUT /products/{id}/generateAIDescription` — AI description

**Categories**: `GET/POST /categories`, `GET/PUT/DELETE /categories/{id}`
- `GET /categories/by-path/find` — Find by URL path
- `POST /categories/update/depths` — Recalculate tree

**Stock**: `GET/POST /stock`, `GET/PUT/DELETE /stock/{id}`, `POST /stock/upsert/bulk`

**Prices**: `GET/POST /prices`, `GET/PUT/DELETE /prices/{id}`, `POST /prices/upsert/bulk`

**Warehouses**: CRUD at `/warehouses`
**Media**: CRUD at `/media`
**Vendors**: CRUD at `/vendors`
**Translations**: CRUD at `/translations`, `PUT /translations/upsert/single`, `PUT /translations/upsert/bulk`, `POST /translations/job/run`, `GET /translations/job/progress`
**Customer Groups**: CRUD at `/customer/groups`

### Product Filters (26 total)

**Standard**: `id`, `name`, `sku`, `status` (draft/private/public), `product_type` (simple/configurable/license/dt-one), `seo_slug`, `_created_at`, `_updated_at`

**Relation**: `stock.warehouse_id`, `stock.stock_quantity`, `defaultStock.stock_quantity`, `price`, `specialPrice`, `finalPrice`, `attributeValues.value.attribute_id`, `attributeValues.value.attribute_value`, `attributeValues.attribute_value_id`, `categories.category_id`

**Callback**: `attribute` (JSON array), `exclude_child_products`, `exclude_parent_products`, `without_stock`, `exclude_child_products_id`, `parent_id`, `search`, `anchor_category_id`

### Product Includes (42+)

**Stock**: `stock`, `stock.warehouse`, `stockLocations`, `stockLocations.warehouse`

**Pricing**: `prices`, `price`, `specialPrice`, `finalPrice`, `costPrice`, `tierPrices`, `finalTierPrices`, `groupPrices`

**Attributes**: `attributeValues`, `attributeValues.value`, `attributeValues.value.translation`, `attributeValues.value.attribute.translation`, `attributeValues.value.attribute.group`

**Media**: `media`, `mainMedia`

**Cross/Up-Sell**: `crossSells`, `crossSells.product`, `crossSells.crossSellProduct`, `upSells`, `upSells.product`, `upSells.upSellProduct`

**Vendor**: `vendorProduct`, `vendorProduct.vendor`

**Variations**: `parentProductAttributes`, `childProducts`, `childProducts.childProduct`, `parentProducts`

**Category/Translation**: `categories`, `categories.category`, `translation`

**License**: `licenseConfiguration`

**Custom Computed**: `attributes` (denormalized summary), `stockSum` (total stock), `variationAttributes` (variation attrs with values)

### Product Validation (Create/Upsert)

- `name`: nullable, string, min:2
- `sku`: nullable, string, max:255, min:2, unique
- `product_type`: nullable, in: simple, configurable, license, dt-one (immutable after creation)
- `status`: nullable, in: draft, private, public
- `visibility`: nullable, in: search_catalog, search, catalog, hidden
- `description`: nullable, string (HTML)
- `short_description`: nullable, string
- `tax_class_id`: nullable, numeric
- `stock`: array of `{warehouse_id, stock_quantity}`
- `prices`: `{price, cost_price, special_price, special_price_start_date, special_price_end_date, tier_prices: [{min_quantity, price}], group_prices: [{customer_group_id, price}]}`
- `attributes`: array of `{attribute_id, value, auto_create_value, is_variation_attribute}`
- `media`: array of `{file, media_type, media_url, alt_text, is_primary, order}`
- `categories`: array of category IDs
- `cross_sells`, `up_sells`: array of product IDs
- `seo`: `{slug, meta_title, meta_description}`
- Upsert: `action` in: createOrUpdate, onlyCreate, onlyUpdate

### Product Types & Variations

- `simple` — Standalone product
- `configurable` — Parent with child variations
- `license` — Product with license key generation
- `dt-one` — Digital product

**Configurable product flow**: Create parent → Attach variation attributes → Generate child variations

---

## OrderHub — `api/v1/apps/order-hub/`

Complete order lifecycle: cart → checkout → order.

### Endpoints

**Orders**: CRUD + `GET /orders/statuses/list`, `GET /orders/statuses/options`, `POST /orders/statuses`, `DELETE /orders/statuses/{status}`

**Line Items**: CRUD at `/order-line-items`

**Order Comments**: CRUD at `/order-comments`

**Carts**: CRUD + `PATCH /carts` (upsert by session_uuid)

**Cart Items**: CRUD at `/cart-items`

**Checkout**: `GET /carts/{cart}/checkout` (preview), `POST /carts/{cart}/checkout` (complete)

**Billing Methods**: CRUD + `GET /billing-methods/payment-providers/templates`, `POST /billing-methods/payment-providers/templates`

**Shipping Methods**: CRUD at `/shipping-methods`

**Customer Payment Methods**: CRUD at `/customer-payment-methods`

**Quotes**: CRUD at `/quotes`, `/quote-items`, `/quote-items-groups`

### Order Filters

`id`, `status` (draft/pending/invoiced/shipped/completed/pending_payment/paid/refunded/partially_refunded/canceled/processing), `total_price`, `customer_id`, `shipping_method_id`, `billing_method_id`, `external_id`, `order_number`, `_created_at`, `_updated_at`

### Order Includes

`customer`, `customer.company`, `shippingMethod`, `billingMethod`, `orderLineItems`, `orderLineItems.product`, `orderLineItems.product.mainMedia`, `orderLineItems.product.media`, `shippingAddress`, `billingAddress`, `comments`, `attributeValues`, `attributeValues.value`, `attributeValues.value.translation`, `attributeValues.value.attribute`

### Cart Includes

`session`, `cartItems`, `cartItems.product`, `cartItems.product.price`, `cartItems.product.specialPrice`, `cartItems.product.finalPrice`, `cartItems.product.tierPrices`, `cartItems.product.finalTierPrices`, `cartItems.product.groupPrices`, `cartItems.product.media`, `cartItems.product.mainMedia`, `cartItems.product.crossSells`, `cartItems.product.upSells`, `customer`, `customer.company`

### Order Validation

- `status`: required, one of the statuses above
- `customer_id`: required, numeric
- `line_items`: required, array, min:1
- `line_items.*.name`: required, string
- `line_items.*.quantity`: required, numeric
- `line_items.*.price`: required, numeric
- `line_items.*.product_id`: optional, numeric

### Checkout Validation

- `shipping_method_id`: required, numeric
- `billing_method_id`: required, numeric
- `shipping_address_id`: required, numeric
- `billing_address_id`: required, numeric
- `comment`: optional, string

### Checkout Flow

1. Create Cart: `POST /carts` or `PATCH /carts` (upsert by session_uuid)
2. Add Items: `POST /cart-items`
3. Preview: `GET /carts/{cart}/checkout`
4. Complete: `POST /carts/{cart}/checkout`
5. Order Created with line items, addresses, payment

---

## CustomerHub — `api/v1/apps/customer-hub/`

B2B customer management with companies.

### Endpoints

**Customers**: CRUD + `PUT /customers/bulk/update`
**Companies**: CRUD at `/companies`
**Shipping Addresses**: CRUD at `/shippingAddresses`
**Billing Addresses**: CRUD at `/billingAddresses`
**Roles**: CRUD at `/roles`
**Customer Groups**: CRUD at `/customerGroups`
**Notes**: CRUD at `/notes`
**Settings**: `GET/POST /settings`, `POST /settings/reset`, per-group

### Customer Filters

`id`, `customer_number`, `first_name`, `last_name`, `email`, `phone`, `company_id`, `company.name`, `company.company_number`, `company.email`, `role_id`, `customer_group_id`, `_created_at`, `_updated_at`, `search` (callback: first_name, last_name, email, customer_number, id, company_id)

### Customer Includes

`company`, `company.companyGroup`, `company.shippingAddresses`, `company.billingAddresses`, `role`, `shippingAddresses`, `billingAddresses`, `customerGroup`, `defaultCustomerShippingAddress`, `defaultCompanyShippingAddress`, `defaultCustomerBillingAddress`, `defaultCompanyBillingAddress`, `attributeValues`, `attributeValues.value`, `attributeValues.value.translation`, `attributeValues.value.attribute.translation`, `attributeValues.value.attribute.group`

### Customer Validation

- `email`: sometimes, email, unique
- `first_name`, `last_name`: string
- `salutation`: in: Mr., Ms., Other
- `status`: in: active, inactive, pending
- `company_id`, `role_id`, `customer_group_id`: numeric, nullable
- `attributes`: array of `{attribute_value_id}`

### Company Validation

- `name`: required, string
- `email`: email, unique
- `country`: string, ValidCountry rule
- `vat_number`, `registration_number`: string, nullable

---

## AttributesHub — `api/v1/apps/attributes-hub/`

Dynamic product attributes with polymorphic relations.

### Endpoints

**Attributes**: CRUD + `PUT /attributes/insert/bulk`, `GET /attributeTypes`
**Attribute Values**: CRUD at `/attributeValues`
**Attribute Groups**: CRUD at `/attributeGroups`, `GET /attributeGroups/types/list`
**Attributable Values**: CRUD at `/attributableValues`

### Attribute Types

`numeric`, `text`, `textarea`, `select`, `multiselect`, `radio`, `boolean`, `date`, `datetime`, `swatch`

### Attribute Filters

`id`, `name`, `type`, `group_id`, `_created_at`, `_updated_at`, `visible_on_the_product_page`, `used_for_filtering`, `filterable_with_results`, `position`, `group.type`

### Attribute Includes

- **Attributes**: `values`, `values.translation`, `translation`, `group`
- **Attribute Values**: `attribute`, `translation`
- **Attribute Groups**: `translation`
- **Attributable Values**: `value`, `value.attribute`, `attributable`

---

## MediaHub — `api/v1/apps/media-hub/`

Polymorphic media management with Bunny CDN.

### Endpoints

- `GET /cdn/{domain}/{path}` — Public CDN proxy (no auth)
- CRUD at `/media`
- `GET /media/{type}/{id}` — Media for specific model
- `GET /media/{type}/{id}/primary` — Primary media
- `POST /media/{id}/primary` — Set as primary
- `POST /media/{id}/sort-order` — Update sort order

### Media Types

`image`, `video`, `document`, `audio`

### Media Filters

`id`, `mediable_type` (Products, Companies, etc.), `mediable_id`, `media_type`, `is_primary`

---

## NotificationHub — `api/v1/apps/notification-hub/`

120+ endpoints. Multi-channel: email, database, broadcast, sms, push, slack.

### Key Endpoints

**Notifications**: CRUD + `POST /{id}/send`, `POST /{id}/resend`, `POST /{id}/mark-read`, `GET /stats`, `GET /unread`, `POST /create-for-user`, `POST /create-bulk` (max 10,000), `POST /create-bulk-for-roles`, `POST /mark-all-read`

**Types**: CRUD + activate/deactivate, channel management, template management, role management, search, variables

**Preferences**: CRUD + per-user enable/disable, channels, frequency, quiet hours, bulk update, reset, export/import

**Attempts**: CRUD + stats, pending, retry, failures, success rates, error codes, per-channel stats

**Dashboard**: `GET /dashboard/overview`, `/channel-performance`, `/recent-activity`, `/error-analysis`, `/user-engagement`, `/system-health`, `/trends`, `/alerts`

**Settings**: Per-group with `POST /settings/{group}/test` for testing channel connections

### Notification Filters

`id`, `notification_type_id`, `status` (pending/sent/failed/partial/read), `priority` (1-10), `notifiable_type`, `notifiable_id`, `creator_type`, `creator_id`, `channels`

### Notification Validation

- `notification_type_id`: required, integer
- `notifiable_type`: required, string
- `notifiable_id`: required, integer
- `title`: required, string, max:255
- `message`: required, string
- `channels`: array, each in: email, database, broadcast, sms, push, slack
- `priority`: integer, min:1, max:10

---

## TaxHub — `api/v1/apps/tax-hub/`

Rule-based tax calculation with jurisdictions.

### Endpoints

**Tax Classes**: CRUD at `/tax-classes`
**Jurisdictions**: CRUD at `/jurisdictions`
**Tax Class Jurisdictions**: CRUD at `/tax-class-jurisdictions` (mappings with rates)
**Tax Rules**: CRUD + `GET /{id}/conditions`, `POST /{id}/conditions`
**Tax Rule Conditions**: `PUT/DELETE /tax-rule-conditions/{id}`
**Calculate**: `POST /calculate`
**Import**: `GET /import/regions`, `POST /import/{region}` (us/eu/non-eu-europe), `POST /import/refresh/all`
**Settings**: Per-group

### Tax Calculation

```json
POST /calculate
{
  "line_items": [
    {"subtotal": 199.99, "tax_class_id": 1, "product_id": 105}
  ],
  "customer": {
    "email": "...",
    "country": "DE",
    "region": "Bavaria",
    "customer_group": "retail",
    "vat_number": "DE123456789"
  }
}
```

**Rate Fallback Chain**: Matched tax rule → Tax class + jurisdiction mapping → Country-level rate → GLOBAL jurisdiction → Config default

**Tax Rule Condition Types**: `customer_email`, `email_domain`, `country`, `region`, `customer_group`, `vat_number`

**Condition Operators**: `equals`, `contains`, `starts_with`, `ends_with`, `in`, `not_in`, `is_empty`, `is_not_empty`

---

## SettingsHub — `api/v1/apps/settings-hub/`

Platform configuration. No includes.

### Endpoints

**Config**: CRUD at `/config`
**Translations**: CRUD at `/translations`
**Reference Data**: `GET /locales`, `GET /countries`, `GET /currencies`
**Cache**: `GET /cache`, `DELETE /clearAppCache/{installationKey}`
**Index**: `GET /index`, `PUT /index/{id}`, `POST /index/queue`

---

## LicenseHub — `api/v1/apps/license-hub/`

License key lifecycle management.

### Endpoints

**License Keys**: CRUD + `GET /license-keys/statuses/list`, `POST /license-keys/import`, `POST /license-keys/generate`, `GET /license-keys/export`, `POST /{id}/activate`, `POST /{id}/deactivate`, `POST /{id}/revoke`, `POST /{id}/validate`, `GET /{id}/status`

**License Pools**: CRUD + `GET /{id}/available-count`, `POST /{id}/assign`
**License Rules**: CRUD + `GET /license-rules/product/{productId}`
**Usage Logs**: CRUD + `GET /license-usage-logs/actions/list`, per-key logs
**Configurations**: CRUD + `GET /license-configurations/product/{productId}`

**Key Statuses**: `available`, `assigned`, `activated`, `expired`, `revoked`

### Key Generation

```json
POST /license-keys/generate
{
  "product_id": 12,
  "template": "XXXX-XXXX-XXXX-XXXX",
  "quantity": 100,
  "mode": "quantity_per_licence"
}
```

`X` = random character placeholder. `allowed_chars` restricts character set.

---

## Bulk Operations Summary

| Hub | Endpoint | Method | Max |
|-----|----------|--------|-----|
| ProductHub | `/products/bulk/update` | PUT | ~1000 |
| ProductHub | `/products/bulk/delete` | DELETE | ~1000 |
| ProductHub | `/products/upsert/single` | PUT | 1 (idempotent) |
| ProductHub | `/stock/upsert/bulk` | POST | ~1000 |
| ProductHub | `/prices/upsert/bulk` | POST | ~1000 |
| ProductHub | `/translations/upsert/bulk` | PUT | ~1000 |
| AttributesHub | `/attributes/insert/bulk` | PUT | ~1000 |
| CustomerHub | `/customers/bulk/update` | PUT | ~1000 |
| NotificationHub | `/notifications/create-bulk` | POST | 10,000 |
| LicenseHub | `/license-keys/generate` | POST | 1,000 |

**Upsert `action` values**: `createOrUpdate` (default), `onlyCreate`, `onlyUpdate`

---

## AI Features

- `PUT /products/{id}/generateAIDescription` — Generates `description` (HTML) and `short_description` from product data
- `POST /translations/job/run` — Trigger AI translation job
- `GET /translations/job/progress` — Check job progress

---

## Code Conventions for Integrations

When writing code that integrates with the DataHub API:

1. **Always set these headers**: `Authorization: Bearer {token}`, `Accept: application/json`, `Content-Type: application/json` (for POST/PUT/PATCH)
2. **Use environment variables** for domain and token: `DATAHUB_DOMAIN` (default: `api.datahub.syncspider.com`), `DATAHUB_TOKEN`
3. **Handle pagination** — iterate through `current_page` to `last_page`
4. **Use upsert endpoints** for sync workflows to avoid duplicate errors
5. **URL-encode filter JSON** properly
6. **Retry only 5xx errors** with exponential backoff; fix 4xx errors before retrying
7. **Use includes judiciously** — only request what you need
8. **Prefer `IN` over chaining `OR`** for multi-value filters
9. **Use `anchor_category_id`** instead of `categories.category_id` when you want to include subcategories
10. **Use `filter[exclude_child_products]=1`** on product listings to hide variation children

## Documentation Files

Detailed documentation for each topic is available in this repository:

- `introduction.mdx` — Platform overview
- `quickstart.mdx` — First API call in 5 minutes
- `authentication.mdx` — Bearer token auth
- `core-concepts/common-patterns.mdx` — Pagination, sorting, response formats
- `core-concepts/filtering.mdx` — Filter syntax and operators
- `core-concepts/includes.mdx` — Include system
- `core-concepts/error-handling.mdx` — Error codes and handling
- `hubs/product-hub.mdx` — ProductHub (most detailed)
- `hubs/order-hub.mdx` — OrderHub
- `hubs/customer-hub.mdx` — CustomerHub
- `hubs/attributes-hub.mdx` — AttributesHub
- `hubs/media-hub.mdx` — MediaHub
- `hubs/notification-hub.mdx` — NotificationHub
- `hubs/tax-hub.mdx` — TaxHub
- `hubs/settings-hub.mdx` — SettingsHub
- `hubs/license-hub.mdx` — LicenseHub
- `advanced/bulk-operations.mdx` — Bulk operations guide
- `advanced/checkout-flow.mdx` — Cart-to-order flow
- `advanced/tax-calculation.mdx` — Tax engine details
- `advanced/product-variations.mdx` — Configurable products
- `advanced/ai-features.mdx` — AI descriptions and translations
- `api-reference/openapi.yaml` — OpenAPI 3.0.0 spec
