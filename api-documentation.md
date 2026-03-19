# DataHub Platform — API Documentation

> Comprehensive API reference for all 9 DataHub hubs with endpoints, filters, includes, validation rules, and curl examples.

---

## Table of Contents

1. [Common Patterns](#common-patterns)
2. [AttributesHub](#1-attributeshub)
3. [CustomerHub](#2-customerhub)
4. [LicenseHub](#3-licensehub)
5. [MediaHub](#4-mediahub)
6. [NotificationHub](#5-notificationhub)
7. [OrderHub](#6-orderhub)
8. [ProductHub](#7-producthub--most-complex-hub)
9. [SettingsHub](#8-settingshub)
10. [TaxHub](#9-taxhub)

---

## Common Patterns

### Authentication

All API endpoints require Bearer token authentication unless explicitly noted otherwise.

```
Authorization: Bearer {api_token}
```

Tokens are obtained through the authentication flow. All hub endpoints are protected by the `auth:api` middleware.

### Base URL

```
https://api.datahub.syncspider.com/api/v1/apps/{hub-slug}/
```

The default API domain is `api.datahub.syncspider.com`. Replace `{hub-slug}` with the kebab-case hub identifier (e.g., `attributes-hub`, `customer-hub`).

### Pagination

All list (index) endpoints return paginated results. Control pagination with these query parameters:

| Parameter  | Type    | Default | Description                     |
|------------|---------|---------|---------------------------------|
| `page`     | integer | 1       | Page number (1-based)           |
| `per_page` | integer | 25      | Items per page (max varies, typically 50–200) |

**Paginated response structure:**

```json
{
  "data": [ ... ],
  "current_page": 1,
  "last_page": 10,
  "per_page": 25,
  "total": 250,
  "from": 1,
  "to": 25
}
```

### Includes (Eager Loading)

Request related resources using the `include` query parameter. Supports nested relationships with dot notation.

```
?include=relation1,relation2,nested.relation
```

**Example:**

```
GET /api/v1/apps/customer-hub/customers?include=company,shippingAddresses,attributeValues.value.translation
```

### Filter System (CommonFilterRepository)

All hubs use `CommonFilterRepository` for MongoDB-compatible filtering via Spatie QueryBuilder. Filters are passed as JSON-encoded arrays of condition objects.

#### Filter Syntax

```
?filter[field_name]=[{"condition":"operator","value":"value"}]
```

#### Supported Operators

| Condition     | Description              | Example                                                                 |
|---------------|--------------------------|-------------------------------------------------------------------------|
| `=`           | Exact match              | `?filter[status]=[{"condition":"=","value":"active"}]`                  |
| `!=`          | Not equal                | `?filter[status]=[{"condition":"!=","value":"deleted"}]`                |
| `>`           | Greater than             | `?filter[price]=[{"condition":">","value":100}]`                       |
| `<`           | Less than                | `?filter[price]=[{"condition":"<","value":500}]`                       |
| `>=`          | Greater than or equal    | `?filter[quantity]=[{"condition":">=","value":10}]`                     |
| `<=`          | Less than or equal       | `?filter[quantity]=[{"condition":"<=","value":100}]`                    |
| `LIKE`        | Pattern match            | `?filter[name]=[{"condition":"LIKE","value":"%search%"}]`              |
| `IN`          | Value in set             | `?filter[status]=[{"condition":"IN","value":["active","pending"]}]`    |
| `NOT IN`      | Value not in set         | `?filter[status]=[{"condition":"NOT IN","value":["canceled"]}]`        |
| `EMPTY`       | Field is null/empty      | `?filter[description]=[{"condition":"EMPTY"}]`                         |
| `NOT EMPTY`   | Field is not null/empty  | `?filter[description]=[{"condition":"NOT EMPTY"}]`                     |

#### Combining Conditions

Multiple conditions on the same field use the `operator` key (`AND` or `OR`):

```
?filter[price]=[{"condition":">=","value":100},{"condition":"<=","value":500,"operator":"AND"}]
```

```
?filter[status]=[{"condition":"=","value":"active"},{"condition":"=","value":"pending","operator":"OR"}]
```

#### Relation Filters

Filter through relationships using dot notation:

```
?filter[company.name]=[{"condition":"LIKE","value":"%Acme%"}]
```

#### Callback/Search Filters

Some repositories define callback filters (e.g., `search`) that query across multiple fields simultaneously:

```
?filter[search]=term
```

#### Filter Field Types

| Type     | Description               | Example Values                          |
|----------|---------------------------|-----------------------------------------|
| `number` | Integer or float values   | `1`, `42`, `3.14`                       |
| `text`   | String values             | `"Product Name"`, `"SKU-001"`           |
| `date`   | Date/DateTime values      | `"2024-01-01"`, `"2024-01-01T10:30:00"` |
| `bool`   | Boolean values            | `true`, `false`, `1`, `0`               |

### Sorting

Sort results using the `sort` query parameter. Prefix with `-` for descending order:

```
?sort=-_created_at,name
```

This sorts by `_created_at` descending, then by `name` ascending.

### Standard Response Formats

**Success (single resource):**

```json
{
  "data": { ... }
}
```

**Success (collection with pagination):**

```json
{
  "data": [ ... ],
  "current_page": 1,
  "last_page": 10,
  "per_page": 25,
  "total": 250
}
```

**Error:**

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "field_name": ["Error description."]
  }
}
```

**HTTP Status Codes:**

| Code | Meaning                |
|------|------------------------|
| 200  | Success                |
| 201  | Created                |
| 204  | Deleted (no content)   |
| 400  | Bad request            |
| 401  | Unauthorized           |
| 403  | Forbidden              |
| 404  | Not found              |
| 422  | Validation error       |
| 500  | Server error           |

---

## 1. AttributesHub

**Base URL:** `api/v1/apps/attributes-hub/`

The AttributesHub manages dynamic product attributes, including attribute definitions, types, values, and groups. It supports polymorphic attributable relations and translations.

### Endpoints

#### Attributes

| Method | Endpoint                         | Description                              |
|--------|----------------------------------|------------------------------------------|
| GET    | `/attributes`                    | List all attributes (paginated, filterable) |
| POST   | `/attributes`                    | Create a new attribute                   |
| GET    | `/attributes/{id}`               | Get a single attribute                   |
| PUT    | `/attributes/{id}`               | Update an attribute                      |
| DELETE | `/attributes/{id}`               | Delete an attribute                      |
| PUT    | `/attributes/insert/bulk`        | Bulk create or update attributes         |
| GET    | `/attributeTypes`                | List available attribute types           |

**Available Attribute Types:** `numeric`, `text`, `textarea`, `select`, `multiselect`, `radio`, `boolean`, `date`, `datetime`, `swatch`

#### Attribute Values

| Method | Endpoint                         | Description                              |
|--------|----------------------------------|------------------------------------------|
| GET    | `/attributeValues`               | List all attribute values                |
| POST   | `/attributeValues`               | Create an attribute value                |
| GET    | `/attributeValues/{id}`          | Get a single attribute value             |
| PUT    | `/attributeValues/{id}`          | Update an attribute value                |
| DELETE | `/attributeValues/{id}`          | Delete an attribute value                |

#### Attribute Groups

| Method | Endpoint                         | Description                              |
|--------|----------------------------------|------------------------------------------|
| GET    | `/attributeGroups`               | List all attribute groups                |
| POST   | `/attributeGroups`               | Create an attribute group                |
| GET    | `/attributeGroups/{id}`          | Get a single attribute group             |
| PUT    | `/attributeGroups/{id}`          | Update an attribute group                |
| DELETE | `/attributeGroups/{id}`          | Delete an attribute group                |
| GET    | `/attributeGroups/types/list`    | List available group types               |

#### Attributable Values

| Method | Endpoint                         | Description                              |
|--------|----------------------------------|------------------------------------------|
| GET    | `/attributableValues`            | List all attributable values             |
| POST   | `/attributableValues`            | Create an attributable value             |
| GET    | `/attributableValues/{id}`       | Get a single attributable value          |
| PUT    | `/attributableValues/{id}`       | Update an attributable value             |
| DELETE | `/attributableValues/{id}`       | Delete an attributable value             |

### Filters

#### Attribute Filters

| Filter Field                       | Type    | Notes                    |
|------------------------------------|---------|--------------------------|
| `id`                               | number  |                          |
| `name`                             | text    |                          |
| `type`                             | text    | One of the attribute types |
| `group_id`                         | number  |                          |
| `_created_at`                      | date    |                          |
| `_updated_at`                      | date    |                          |
| `visible_on_the_product_page`      | bool    |                          |
| `used_for_filtering`               | bool    |                          |
| `filterable_with_results`          | bool    |                          |
| `position`                         | number  |                          |
| `group.type`                       | text    | Relation filter (group)  |

#### Attribute Value Filters

| Filter Field                                  | Type    | Notes                       |
|-----------------------------------------------|---------|-----------------------------|
| `id`                                          | number  |                             |
| `attribute_id`                                | number  |                             |
| `value`                                       | text    |                             |
| `swatch_value`                                | text    |                             |
| `attribute.visible_on_the_product_page`       | bool    | Relation filter (attribute) |
| `attribute.used_for_filtering`                | bool    | Relation filter (attribute) |
| `attribute.filterable_with_results`           | bool    | Relation filter (attribute) |
| `attribute.type`                              | text    | Relation filter (attribute) |
| `attribute.group_id`                          | number  | Relation filter (attribute) |

#### Attribute Group Filters

| Filter Field     | Type    | Notes |
|------------------|---------|-------|
| `id`             | number  |       |
| `name`           | text    |       |
| `display_order`  | number  |       |
| `type`           | text    |       |

#### Attributable Value Filters

| Filter Field         | Type    | Notes |
|----------------------|---------|-------|
| `id`                 | number  |       |
| `attributable_id`    | number  |       |
| `attributable_type`  | text    |       |
| `attribute_value_id` | number  |       |

### Includes

| Resource            | Available Includes                                      |
|---------------------|---------------------------------------------------------|
| **Attributes**      | `values`, `values.translation`, `translation`, `group`  |
| **Attribute Values** | `attribute`, `translation`                             |
| **Attribute Groups** | `translation`                                          |
| **Attributable Values** | `value`, `value.attribute`, `attributable`          |

### Validation Rules

#### Create Attribute — `POST /attributes`

| Field                          | Rules                                          |
|--------------------------------|------------------------------------------------|
| `name`                         | required, string, unique per type              |
| `type`                         | required, string (one of available types)      |
| `group_id`                     | required, numeric                              |
| `display_options`              | sometimes, json                                |
| `visible_on_the_product_page`  | sometimes, boolean                             |
| `used_for_filtering`           | sometimes, boolean                             |
| `filterable_with_results`      | sometimes, boolean                             |
| `required`                     | sometimes, boolean                             |
| `position`                     | sometimes, numeric                             |
| `meta_data`                    | sometimes, array                               |

#### Create Attribute Value — `POST /attributeValues`

| Field                          | Rules                                          |
|--------------------------------|------------------------------------------------|
| `attribute_id`                 | required, numeric                              |
| `value`                        | required                                       |
| `meta_data.definition_values`  | sometimes, array                               |

#### Create Attribute Group — `POST /attributeGroups`

| Field           | Rules                                          |
|-----------------|------------------------------------------------|
| `name`          | required, string                               |
| `type`          | required, string, in: `dynamic`                |
| `display_order` | sometimes, numeric                             |

#### Bulk Create/Update — `PUT /attributes/insert/bulk`

Each item in the array requires: `name` (required, string), `type` (required, string), `group_id` (required, numeric), plus all optional fields from the single create endpoint.

### Examples

#### 1. List attributes with filter and include

```bash
curl -X GET \
  'https://example.com/api/v1/apps/attributes-hub/attributes?filter[type]=[{"condition":"=","value":"select"}]&include=values,group&per_page=10&sort=position' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Accept: application/json'
```

#### 2. Create a new attribute

```bash
curl -X POST \
  'https://example.com/api/v1/apps/attributes-hub/attributes' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "name": "Material",
    "type": "select",
    "group_id": 1,
    "visible_on_the_product_page": true,
    "used_for_filtering": true,
    "filterable_with_results": true,
    "required": false,
    "position": 5
  }'
```

#### 3. Get attribute values for a specific attribute

```bash
curl -X GET \
  'https://example.com/api/v1/apps/attributes-hub/attributeValues?filter[attribute_id]=[{"condition":"=","value":42}]&include=attribute,translation&sort=value' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Accept: application/json'
```

#### 4. Bulk create attributes

```bash
curl -X PUT \
  'https://example.com/api/v1/apps/attributes-hub/attributes/insert/bulk' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '[
    {
      "name": "Weight",
      "type": "numeric",
      "group_id": 2,
      "position": 1
    },
    {
      "name": "Dimensions",
      "type": "text",
      "group_id": 2,
      "position": 2
    },
    {
      "name": "Color",
      "type": "swatch",
      "group_id": 1,
      "position": 3,
      "visible_on_the_product_page": true,
      "used_for_filtering": true
    }
  ]'
```

#### 5. Filter visible and filterable attributes

```bash
curl -X GET \
  'https://example.com/api/v1/apps/attributes-hub/attributes?filter[visible_on_the_product_page]=[{"condition":"=","value":true}]&filter[used_for_filtering]=[{"condition":"=","value":true}]&include=values.translation,group&sort=-position' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Accept: application/json'
```

---

## 2. CustomerHub

**Base URL:** `api/v1/apps/customer-hub/`

The CustomerHub manages customers, companies, addresses, roles, customer groups, and notes. It integrates with AttributesHub for custom customer/company attributes and provides a settings system via HubSettingsTrait.

### Endpoints

#### Settings

| Method | Endpoint                        | Description                              |
|--------|---------------------------------|------------------------------------------|
| GET    | `/settings/groups/list`         | List all settings groups                 |
| GET    | `/settings`                     | Get all settings                         |
| POST   | `/settings`                     | Update settings                          |
| POST   | `/settings/reset`               | Reset all settings to defaults           |
| GET    | `/settings/{group}`             | Get settings for a specific group        |
| POST   | `/settings/{group}`             | Update settings for a specific group     |
| POST   | `/settings/{group}/reset`       | Reset a specific group to defaults       |

#### Companies

| Method | Endpoint                        | Description                              |
|--------|---------------------------------|------------------------------------------|
| GET    | `/companies`                    | List all companies (paginated, filterable) |
| POST   | `/companies`                    | Create a new company                     |
| GET    | `/companies/{id}`               | Get a single company                     |
| PUT    | `/companies/{id}`               | Update a company                         |
| DELETE | `/companies/{id}`               | Delete a company                         |

#### Customers

| Method | Endpoint                        | Description                              |
|--------|---------------------------------|------------------------------------------|
| GET    | `/customers`                    | List all customers (paginated, filterable) |
| POST   | `/customers`                    | Create a new customer                    |
| GET    | `/customers/{id}`               | Get a single customer                    |
| PUT    | `/customers/{id}`               | Update a customer                        |
| DELETE | `/customers/{id}`               | Delete a customer                        |
| PUT    | `/customers/bulk/update`        | Bulk update customers                    |

#### Notes

| Method | Endpoint                        | Description                              |
|--------|---------------------------------|------------------------------------------|
| GET    | `/notes`                        | List all notes                           |
| POST   | `/notes`                        | Create a new note                        |
| GET    | `/notes/{id}`                   | Get a single note                        |
| PUT    | `/notes/{id}`                   | Update a note                            |
| DELETE | `/notes/{id}`                   | Delete a note                            |

#### Roles

| Method | Endpoint                        | Description                              |
|--------|---------------------------------|------------------------------------------|
| GET    | `/roles`                        | List all roles                           |
| POST   | `/roles`                        | Create a new role                        |
| GET    | `/roles/{id}`                   | Get a single role                        |
| PUT    | `/roles/{id}`                   | Update a role                            |
| DELETE | `/roles/{id}`                   | Delete a role                            |

#### Shipping Addresses

| Method | Endpoint                        | Description                              |
|--------|---------------------------------|------------------------------------------|
| GET    | `/shippingAddresses`            | List all shipping addresses              |
| POST   | `/shippingAddresses`            | Create a shipping address                |
| GET    | `/shippingAddresses/{id}`       | Get a single shipping address            |
| PUT    | `/shippingAddresses/{id}`       | Update a shipping address                |
| DELETE | `/shippingAddresses/{id}`       | Delete a shipping address                |

#### Billing Addresses

| Method | Endpoint                        | Description                              |
|--------|---------------------------------|------------------------------------------|
| GET    | `/billingAddresses`             | List all billing addresses               |
| POST   | `/billingAddresses`             | Create a billing address                 |
| GET    | `/billingAddresses/{id}`        | Get a single billing address             |
| PUT    | `/billingAddresses/{id}`        | Update a billing address                 |
| DELETE | `/billingAddresses/{id}`        | Delete a billing address                 |

#### Customer Groups

| Method | Endpoint                        | Description                              |
|--------|---------------------------------|------------------------------------------|
| GET    | `/customerGroups`               | List all customer groups                 |
| POST   | `/customerGroups`               | Create a customer group                  |
| GET    | `/customerGroups/{id}`          | Get a single customer group              |
| PUT    | `/customerGroups/{id}`          | Update a customer group                  |
| DELETE | `/customerGroups/{id}`          | Delete a customer group                  |

### Filters

#### Customer Filters

| Filter Field              | Type     | Notes                                                   |
|---------------------------|----------|---------------------------------------------------------|
| `id`                      | number   |                                                         |
| `customer_number`         | text     |                                                         |
| `first_name`              | text     |                                                         |
| `last_name`               | text     |                                                         |
| `email`                   | text     |                                                         |
| `phone`                   | text     |                                                         |
| `company_id`              | number   |                                                         |
| `company.name`            | text     | Relation filter (company)                               |
| `company.company_number`  | text     | Relation filter (company)                               |
| `company.email`           | text     | Relation filter (company)                               |
| `role_id`                 | number   |                                                         |
| `customer_group_id`       | number   |                                                         |
| `_created_at`             | date     |                                                         |
| `_updated_at`             | date     |                                                         |
| `search`                  | callback | Searches: first_name, last_name, email, customer_number, id, company_id |

#### Company Filters

| Filter Field      | Type   | Notes |
|-------------------|--------|-------|
| `id`              | number |       |
| `company_number`  | text   |       |
| `name`            | text   |       |
| `email`           | text   |       |
| `vat_number`      | text   |       |
| `_created_at`     | date   |       |
| `_updated_at`     | date   |       |

#### Note Filters

| Filter Field   | Type   | Notes |
|----------------|--------|-------|
| `id`           | number |       |
| `model`        | text   | e.g., `Companies`, `Customers` |
| `model_id`     | text   |       |
| `_created_at`  | date   |       |
| `_updated_at`  | date   |       |

#### Role Filters

| Filter Field   | Type   | Notes |
|----------------|--------|-------|
| `id`           | number |       |
| `code`         | text   |       |
| `name`         | text   |       |
| `type`         | text   |       |
| `_created_at`  | date   |       |
| `_updated_at`  | date   |       |

#### Shipping/Billing Address Filters

| Filter Field    | Type   | Notes |
|-----------------|--------|-------|
| `id`            | number |       |
| `name`          | text   |       |
| `address_line_1`| text  |       |
| `address_line_2`| text  |       |
| `city`          | text   |       |
| `zip`           | text   |       |
| `state`         | text   |       |
| `type`          | text   |       |
| `country`       | text   |       |
| `customer_id`   | number |       |
| `company_id`    | number |       |
| `_created_at`   | date   |       |
| `_updated_at`   | date   |       |

#### Customer Group Filters

| Filter Field   | Type   | Notes |
|----------------|--------|-------|
| `id`           | number |       |
| `name`         | text   |       |
| `type`         | text   |       |
| `description`  | text   |       |
| `_created_at`  | date   |       |
| `_updated_at`  | date   |       |

### Includes

#### Customer Includes

| Include Path                                      | Description                                    |
|---------------------------------------------------|------------------------------------------------|
| `company`                                         | Parent company                                 |
| `company.companyGroup`                            | Company's group                                |
| `company.shippingAddresses`                       | Company shipping addresses                     |
| `company.billingAddresses`                        | Company billing addresses                      |
| `role`                                            | Customer's role                                |
| `shippingAddresses`                               | Customer's shipping addresses                  |
| `billingAddresses`                                | Customer's billing addresses                   |
| `customerGroup`                                   | Customer's group                               |
| `defaultCustomerShippingAddress`                  | Default shipping address (customer level)      |
| `defaultCompanyShippingAddress`                   | Default shipping address (company level)       |
| `defaultCustomerBillingAddress`                   | Default billing address (customer level)       |
| `defaultCompanyBillingAddress`                    | Default billing address (company level)        |
| `attributeValues`                                 | Custom attribute values                        |
| `attributeValues.value`                           | Attribute value details                        |
| `attributeValues.value.translation`               | Value translations                             |
| `attributeValues.value.attribute.translation`     | Attribute translations                         |
| `attributeValues.value.attribute.group`           | Attribute group                                |

#### Company Includes

| Include Path                           | Description                          |
|----------------------------------------|--------------------------------------|
| `customers`                            | Company's customers                  |
| `customers.shippingAddresses`          | Customers' shipping addresses        |
| `customers.billingAddresses`           | Customers' billing addresses         |
| `shippingAddresses`                    | Company shipping addresses           |
| `billingAddresses`                     | Company billing addresses            |
| `attributeValues`                      | Custom attribute values              |
| `attributeValues.value`               | Attribute value details              |
| `attributeValues.value.translation`   | Value translations                   |
| `attributeValues.value.attribute.translation` | Attribute translations        |
| `attributeValues.value.attribute.group` | Attribute group                    |

#### Shipping/Billing Address Includes

| Include Path | Description          |
|--------------|----------------------|
| `customer`   | Parent customer      |

### Validation Rules

#### Create Customer — `POST /customers`

| Field               | Rules                                                    |
|---------------------|----------------------------------------------------------|
| `customer_number`   | sometimes, string, unique (MongoDB)                      |
| `email`             | sometimes, email, unique (MongoDB)                       |
| `phone`             | string, nullable, unique (MongoDB)                       |
| `first_name`        | string                                                   |
| `last_name`         | string                                                   |
| `salutation`        | in: `Mr.`, `Ms.`, `Other`                               |
| `status`            | in: `active`, `inactive`, `pending`                      |
| `password`          | string                                                   |
| `company_id`        | numeric, nullable                                        |
| `role_id`           | numeric, nullable                                        |
| `customer_group_id` | numeric, nullable                                        |
| `attributes`        | array, nullable                                          |

#### Create Company — `POST /companies`

| Field                | Rules                                                   |
|----------------------|---------------------------------------------------------|
| `name`               | required, string                                        |
| `company_number`     | string, unique (MongoDB)                                |
| `email`              | email, unique (MongoDB)                                 |
| `website`            | string, nullable                                        |
| `phone`              | string, nullable                                        |
| `address_line_1`     | string                                                  |
| `city`               | string                                                  |
| `zip`                | string                                                  |
| `country`            | string, ValidCountry rule                               |
| `vat_number`         | string, nullable                                        |
| `registration_number`| string, nullable                                        |
| `attributes`         | array, nullable                                         |

#### Create Note — `POST /notes`

| Field      | Rules                                                      |
|------------|------------------------------------------------------------|
| `model`    | required, string, in: `Companies`, `Customers`             |
| `model_id` | required, string                                           |
| `note`     | required, string                                           |

### Examples

#### 1. Search customers across multiple fields

```bash
curl -X GET \
  'https://example.com/api/v1/apps/customer-hub/customers?filter[search]=john&include=company,role,customerGroup&per_page=20&sort=-_created_at' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Accept: application/json'
```

#### 2. Filter customers by company name (relation filter)

```bash
curl -X GET \
  'https://example.com/api/v1/apps/customer-hub/customers?filter[company.name]=[{"condition":"LIKE","value":"%Acme%"}]&include=company,shippingAddresses,billingAddresses' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Accept: application/json'
```

#### 3. Create a new customer

```bash
curl -X POST \
  'https://example.com/api/v1/apps/customer-hub/customers' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane.doe@example.com",
    "phone": "+1-555-0123",
    "salutation": "Ms.",
    "status": "active",
    "company_id": 15,
    "role_id": 2,
    "customer_group_id": 3,
    "attributes": [
      {"attribute_value_id": 101},
      {"attribute_value_id": 205}
    ]
  }'
```

#### 4. Filter companies with VAT number

```bash
curl -X GET \
  'https://example.com/api/v1/apps/customer-hub/companies?filter[vat_number]=[{"condition":"NOT EMPTY"}]&include=customers,shippingAddresses,billingAddresses&sort=name' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Accept: application/json'
```

#### 5. Filter customers by date range

```bash
curl -X GET \
  'https://example.com/api/v1/apps/customer-hub/customers?filter[_created_at]=[{"condition":">=","value":"2024-01-01"},{"condition":"<=","value":"2024-06-30","operator":"AND"}]&include=company,attributeValues.value.translation&per_page=50&sort=-_created_at' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Accept: application/json'
```

---

## 3. LicenseHub

**Base URL:** `api/v1/apps/license-hub/`

The LicenseHub provides complete license key lifecycle management including generation, activation, deactivation, revocation, pools, rules, usage tracking, and configurations.

### Endpoints

#### License Keys

| Method | Endpoint                                | Description                              |
|--------|-----------------------------------------|------------------------------------------|
| GET    | `/license-keys`                         | List all license keys (paginated, filterable) |
| POST   | `/license-keys`                         | Create a license key                     |
| GET    | `/license-keys/{id}`                    | Get a single license key                 |
| PUT    | `/license-keys/{id}`                    | Update a license key                     |
| DELETE | `/license-keys/{id}`                    | Delete a license key                     |
| GET    | `/license-keys/statuses/list`           | List all possible statuses               |
| POST   | `/license-keys/import`                  | Import license keys from CSV             |
| POST   | `/license-keys/generate`                | Generate license keys                    |
| GET    | `/license-keys/export`                  | Export license keys                      |
| POST   | `/license-keys/{id}/activate`           | Activate a license key                   |
| POST   | `/license-keys/{id}/deactivate`         | Deactivate a license key                 |
| POST   | `/license-keys/{id}/revoke`             | Revoke a license key                     |
| POST   | `/license-keys/{id}/validate`           | Validate a license key                   |
| GET    | `/license-keys/{id}/status`             | Get current status of a license key      |

**License Key Statuses:** `available`, `assigned`, `activated`, `expired`, `revoked`

#### License Pools

| Method | Endpoint                                | Description                              |
|--------|-----------------------------------------|------------------------------------------|
| GET    | `/license-pools`                        | List all license pools                   |
| POST   | `/license-pools`                        | Create a license pool                    |
| GET    | `/license-pools/{id}`                   | Get a single license pool                |
| PUT    | `/license-pools/{id}`                   | Update a license pool                    |
| DELETE | `/license-pools/{id}`                   | Delete a license pool                    |
| GET    | `/license-pools/{id}/available-count`   | Get count of available keys in pool      |
| POST   | `/license-pools/{id}/assign`            | Assign a key from the pool               |

#### License Rules

| Method | Endpoint                                | Description                              |
|--------|-----------------------------------------|------------------------------------------|
| GET    | `/license-rules`                        | List all license rules                   |
| POST   | `/license-rules`                        | Create a license rule                    |
| GET    | `/license-rules/{id}`                   | Get a single license rule                |
| PUT    | `/license-rules/{id}`                   | Update a license rule                    |
| DELETE | `/license-rules/{id}`                   | Delete a license rule                    |
| GET    | `/license-rules/product/{productId}`    | Get rules for a specific product         |

#### License Usage Logs

| Method | Endpoint                                              | Description                              |
|--------|-------------------------------------------------------|------------------------------------------|
| GET    | `/license-usage-logs`                                 | List all usage logs                      |
| POST   | `/license-usage-logs`                                 | Create a usage log entry                 |
| GET    | `/license-usage-logs/actions/list`                    | List available log actions               |
| GET    | `/license-usage-logs/license-key/{id}`                | Get logs for a specific license key      |
| GET    | `/license-usage-logs/license-key/{id}/activation-count` | Get activation count for a key        |
| GET    | `/license-usage-logs/license-key/{id}/recent`         | Get recent logs for a key                |

#### License Configurations

| Method | Endpoint                                        | Description                              |
|--------|-------------------------------------------------|------------------------------------------|
| GET    | `/license-configurations`                       | List all configurations                  |
| POST   | `/license-configurations`                       | Create a configuration                   |
| GET    | `/license-configurations/{id}`                  | Get a single configuration               |
| PUT    | `/license-configurations/{id}`                  | Update a configuration                   |
| DELETE | `/license-configurations/{id}`                  | Delete a configuration                   |
| GET    | `/license-configurations/product/{productId}`   | Get config for a specific product        |

### Filters

#### License Key Filters

| Filter Field      | Type   | Notes                                        |
|-------------------|--------|----------------------------------------------|
| `id`              | number |                                              |
| `product_id`      | number |                                              |
| `order_id`        | number |                                              |
| `status`          | text   | available, assigned, activated, expired, revoked |
| `license_key`     | text   |                                              |
| `assigned_to`     | text   |                                              |
| `expiration_date` | date   |                                              |
| `activations`     | number |                                              |

#### License Pool Filters

| Filter Field  | Type   | Notes |
|---------------|--------|-------|
| `id`          | number |       |
| `product_id`  | number |       |
| `name`        | text   |       |
| `auto_assign` | bool   |       |

#### License Rule Filters

| Filter Field      | Type   | Notes |
|-------------------|--------|-------|
| `id`              | number |       |
| `product_id`      | number |       |
| `activation_limit`| number |       |
| `expiration_days` | number |       |
| `reassignable`    | bool   |       |

#### Usage Log Filters

| Filter Field      | Type   | Notes |
|-------------------|--------|-------|
| `id`              | number |       |
| `license_key_id`  | number |       |
| `action`          | text   |       |
| `ip_address`      | text   |       |
| `domain`          | text   |       |
| `created_at`      | date   |       |

#### Configuration Filters

| Filter Field  | Type   | Notes |
|---------------|--------|-------|
| `product_id`  | number |       |
| `template`    | text   |       |
| `mode`        | text   |       |

### Includes

| Resource               | Available Includes                            |
|------------------------|-----------------------------------------------|
| **License Keys**       | `usageLogs`, `pool`, `product`, `order`       |
| **License Pools**      | `licenseKeys`, `rules`, `product`             |
| **License Rules**      | `pool`, `product`                             |
| **Usage Logs**         | `licenseKey`                                  |
| **Configurations**     | `product`                                     |

### Validation Rules

#### Create License Key — `POST /license-keys`

| Field              | Rules                                                   |
|--------------------|---------------------------------------------------------|
| `product_id`       | required, integer                                       |
| `license_key`      | required, string, unique (MongoDB)                      |
| `status`           | sometimes, in: `available`, `assigned`, `activated`, `expired`, `revoked` |
| `order_id`         | nullable, integer                                       |
| `assigned_to`      | nullable, string                                        |
| `expiration_date`  | nullable, date                                          |
| `activation_limit` | nullable, integer, min: 1                               |

#### Generate License Keys — `POST /license-keys/generate`

| Field           | Rules                                                      |
|-----------------|-----------------------------------------------------------|
| `product_id`    | required, integer                                          |
| `template`      | required, string                                           |
| `allowed_chars` | sometimes, string                                          |
| `quantity`       | required, integer, min: 1, max: 1000                      |
| `mode`          | sometimes, in: `quantity_per_licence`, `single_licence_quantity` |

#### Create License Pool — `POST /license-pools`

| Field         | Rules                                                     |
|---------------|----------------------------------------------------------|
| `name`        | required, string                                          |
| `product_id`  | required, integer                                         |
| `auto_assign` | sometimes, boolean                                        |

#### Create License Rule — `POST /license-rules`

| Field              | Rules                                                  |
|--------------------|--------------------------------------------------------|
| `product_id`       | required, integer                                      |
| `activation_limit` | sometimes, integer, min: 1                             |
| `expiration_days`  | nullable, integer, min: 1                              |
| `reassignable`     | sometimes, boolean                                     |

#### Create Usage Log — `POST /license-usage-logs`

| Field            | Rules                                                    |
|------------------|----------------------------------------------------------|
| `license_key_id` | required, integer                                        |
| `action`         | required, string (from available actions enum)           |
| `ip_address`     | nullable, string                                         |
| `domain`         | nullable, string                                         |

### Examples

#### 1. List active license keys with includes

```bash
curl -X GET \
  'https://example.com/api/v1/apps/license-hub/license-keys?filter[status]=[{"condition":"=","value":"activated"}]&include=usageLogs,pool,product&per_page=25&sort=-expiration_date' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Accept: application/json'
```

#### 2. Generate license keys from a template

```bash
curl -X POST \
  'https://example.com/api/v1/apps/license-hub/license-keys/generate' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "product_id": 42,
    "template": "XXXX-XXXX-XXXX-XXXX",
    "allowed_chars": "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    "quantity": 100,
    "mode": "quantity_per_licence"
  }'
```

#### 3. Activate a license key

```bash
curl -X POST \
  'https://example.com/api/v1/apps/license-hub/license-keys/157/activate' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "ip_address": "192.168.1.100",
    "domain": "app.customer-site.com"
  }'
```

#### 4. Get usage logs for a specific license key

```bash
curl -X GET \
  'https://example.com/api/v1/apps/license-hub/license-usage-logs/license-key/157?include=licenseKey&sort=-created_at&per_page=50' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Accept: application/json'
```

#### 5. Filter license keys expiring within 30 days

```bash
curl -X GET \
  'https://example.com/api/v1/apps/license-hub/license-keys?filter[status]=[{"condition":"IN","value":["activated","assigned"]}]&filter[expiration_date]=[{"condition":"<=","value":"2024-08-15"},{"condition":">=","value":"2024-07-15","operator":"AND"}]&include=product,pool&sort=expiration_date' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Accept: application/json'
```

---

## 4. MediaHub

**Base URL:** `api/v1/apps/media-hub/`

The MediaHub manages polymorphic media associations (images, videos, documents, audio) and provides a public CDN proxy endpoint for Bunny CDN signed URLs.

### Endpoints

#### CDN Proxy (Public — No Authentication)

| Method | Endpoint                     | Description                              |
|--------|------------------------------|------------------------------------------|
| GET    | `/cdn/{domain}/{path}`       | Public CDN proxy with Bunny CDN signed URLs |

> **Note:** The CDN proxy endpoint does NOT require authentication. The `{domain}` parameter is validated against a regex pattern and `{path}` is a catch-all parameter.

#### Media Management

| Method | Endpoint                       | Description                              |
|--------|--------------------------------|------------------------------------------|
| GET    | `/media`                       | List all media (paginated, filterable)   |
| POST   | `/media`                       | Create/upload a media record             |
| GET    | `/media/{id}`                  | Get a single media record                |
| PUT    | `/media/{id}`                  | Update a media record                    |
| DELETE | `/media/{id}`                  | Delete a media record                    |
| GET    | `/media/{type}/{id}`           | Get all media for a specific model       |
| GET    | `/media/{type}/{id}/primary`   | Get primary media for a specific model   |
| POST   | `/media/{id}/primary`          | Set a media record as primary            |
| POST   | `/media/{id}/sort-order`       | Update the sort order of a media record  |

### Filters

| Filter Field    | Type   | Notes                                       |
|-----------------|--------|---------------------------------------------|
| `id`            | number |                                             |
| `mediable_type` | text   | Polymorphic type (e.g., `Products`, `Companies`) |
| `mediable_id`   | number | ID of the parent model                      |
| `media_type`    | text   | `image`, `video`, `document`, `audio`       |
| `is_primary`    | bool   |                                             |

### Includes

| Resource   | Available Includes |
|------------|-------------------|
| **Media**  | `mediable`        |

### Validation Rules

#### Create Media — `POST /media`

| Field          | Rules                                                    |
|----------------|----------------------------------------------------------|
| `mediable_type` | required, string                                        |
| `mediable_id`  | required, integer                                        |
| `media_type`   | required, in: `image`, `video`, `document`, `audio`      |
| `media_url`    | nullable, url                                            |
| `alt_text`     | nullable, string                                         |
| `is_primary`   | sometimes, boolean                                       |
| `sort_order`   | sometimes, integer, min: 0                               |

### Examples

#### 1. Access media via CDN proxy (public, no auth)

```bash
curl -X GET \
  'https://example.com/api/v1/apps/media-hub/cdn/cdn.example-storage.com/products/images/product-42-hero.jpg'
```

#### 2. List all media for a specific product

```bash
curl -X GET \
  'https://example.com/api/v1/apps/media-hub/media?filter[mediable_type]=[{"condition":"=","value":"Products"}]&filter[mediable_id]=[{"condition":"=","value":42}]&sort=sort_order' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Accept: application/json'
```

#### 3. Filter primary images only

```bash
curl -X GET \
  'https://example.com/api/v1/apps/media-hub/media?filter[media_type]=[{"condition":"=","value":"image"}]&filter[is_primary]=[{"condition":"=","value":true}]&include=mediable&per_page=50' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Accept: application/json'
```

---

## 5. NotificationHub

**Base URL:** `api/v1/apps/notification-hub/`

The NotificationHub is the most feature-rich hub with 120+ endpoints. It provides complete notification lifecycle management across multiple channels (email, SMS, push, Slack, broadcast, database), notification types with templates, user preferences, delivery attempt tracking, and a comprehensive analytics dashboard.

### Endpoints

#### Settings

| Method | Endpoint                       | Description                              |
|--------|--------------------------------|------------------------------------------|
| GET    | `/settings/groups/list`        | List all settings groups                 |
| GET    | `/settings`                    | Get all settings                         |
| POST   | `/settings`                    | Update settings                          |
| POST   | `/settings/reset`              | Reset all settings to defaults           |
| GET    | `/settings/{group}`            | Get settings for a specific group        |
| POST   | `/settings/{group}`            | Update settings for a specific group     |
| POST   | `/settings/{group}/test`       | Test a channel connection (email, sms, push, slack, broadcast, database) |
| POST   | `/settings/{group}/reset`      | Reset a specific group to defaults       |

#### Dashboard

| Method | Endpoint                               | Description                                   |
|--------|----------------------------------------|-----------------------------------------------|
| GET    | `/dashboard/overview`                  | Overall notification statistics                |
| GET    | `/dashboard/channel-performance`       | Performance metrics by channel (query: `days` 1–365) |
| GET    | `/dashboard/recent-activity`           | Recent notification activity (query: `hours` 1–168) |
| GET    | `/dashboard/error-analysis`            | Analysis of notification failures              |
| GET    | `/dashboard/user-engagement`           | User engagement metrics                        |
| GET    | `/dashboard/system-health`             | System health indicators                       |
| GET    | `/dashboard/trends`                    | Notification trends over time                  |
| GET    | `/dashboard/alerts`                    | Active system alerts                           |

#### Notifications

| Method | Endpoint                               | Description                                   |
|--------|----------------------------------------|-----------------------------------------------|
| GET    | `/notifications`                       | List notifications (paginated, filterable)     |
| POST   | `/notifications`                       | Create a notification                          |
| GET    | `/notifications/{id}`                  | Get a single notification                      |
| PUT    | `/notifications/{id}`                  | Update a notification                          |
| DELETE | `/notifications/{id}`                  | Delete a notification                          |
| POST   | `/notifications/{id}/send`             | Send/dispatch a notification                   |
| POST   | `/notifications/{id}/resend`           | Resend a failed notification                   |
| POST   | `/notifications/{id}/mark-read`        | Mark notification as read                      |
| GET    | `/notifications/stats`                 | Notification statistics                        |
| GET    | `/notifications/unread`                | Get unread notifications                       |
| POST   | `/notifications/create-for-user`       | Create a notification for a specific user      |
| POST   | `/notifications/create-bulk`           | Bulk create notifications (max 10,000)         |
| POST   | `/notifications/create-bulk-for-roles` | Bulk create notifications for role members     |
| POST   | `/notifications/mark-all-read`         | Mark all notifications as read                 |

#### Notification Types

| Method | Endpoint                                        | Description                                   |
|--------|-------------------------------------------------|-----------------------------------------------|
| GET    | `/types`                                        | List notification types                        |
| POST   | `/types`                                        | Create a notification type                     |
| GET    | `/types/{id}`                                   | Get a single notification type                 |
| PUT    | `/types/{id}`                                   | Update a notification type                     |
| DELETE | `/types/{id}`                                   | Delete a notification type                     |
| GET    | `/types/active`                                 | List active notification types                 |
| GET    | `/types/user-configurable`                      | List user-configurable types                   |
| GET    | `/types/channel/{channel}`                      | List types for a specific channel              |
| GET    | `/types/stats`                                  | Type statistics                                |
| GET    | `/types/variables`                              | List all template variables                    |
| GET    | `/types/variables/{slug}`                       | Get variables for a specific type              |
| POST   | `/types/variables/validate`                     | Validate template variables                    |
| POST   | `/types/create-predefined`                      | Create a predefined notification type          |
| POST   | `/types/search`                                 | Search notification types                      |
| POST   | `/types/validate-template`                      | Validate a notification template               |
| POST   | `/types/bulk-activate`                          | Bulk activate types                            |
| POST   | `/types/bulk-deactivate`                        | Bulk deactivate types                          |
| POST   | `/types/roles`                                  | Get types by role codes                        |
| GET    | `/types/role/{roleCode}`                        | Get types for a specific role                  |
| POST   | `/types/{id}/activate`                          | Activate a notification type                   |
| POST   | `/types/{id}/deactivate`                        | Deactivate a notification type                 |
| POST   | `/types/{id}/add-channel`                       | Add a channel to a type                        |
| POST   | `/types/{id}/remove-channel`                    | Remove a channel from a type                   |
| POST   | `/types/{id}/update-template`                   | Update the template for a type                 |
| POST   | `/types/{id}/add-role`                          | Add a role to a type                           |
| POST   | `/types/{id}/remove-role`                       | Remove a role from a type                      |
| POST   | `/types/{id}/set-roles`                         | Set roles for a type (replaces all)            |
| POST   | `/types/{id}/make-global`                       | Make a type globally scoped                    |
| POST   | `/types/{id}/make-specific`                     | Make a type specifically scoped                |

#### Preferences

| Method | Endpoint                                        | Description                                   |
|--------|-------------------------------------------------|-----------------------------------------------|
| GET    | `/preferences`                                  | List all preferences                           |
| POST   | `/preferences`                                  | Create a preference                            |
| GET    | `/preferences/{id}`                             | Get a single preference                        |
| PUT    | `/preferences/{id}`                             | Update a preference                            |
| DELETE | `/preferences/{id}`                             | Delete a preference                            |
| GET    | `/preferences/stats`                            | Preference statistics                          |
| GET    | `/preferences/channel-stats`                    | Channel preference statistics                  |
| GET    | `/preferences/for-user`                         | Get preferences for a specific user            |
| GET    | `/preferences/enabled-for-user`                 | Get enabled preferences for a user             |
| GET    | `/preferences/users-for-digest`                 | Get users subscribed to digest delivery        |
| GET    | `/preferences/users-in-quiet-hours`             | Get users currently in quiet hours             |
| POST   | `/preferences/enable-for-user`                  | Enable a preference for a user                 |
| POST   | `/preferences/disable-for-user`                 | Disable a preference for a user                |
| POST   | `/preferences/add-channel-for-user`             | Add a channel for a user preference            |
| POST   | `/preferences/remove-channel-for-user`          | Remove a channel from a user preference        |
| POST   | `/preferences/set-frequency-for-user`           | Set notification frequency for a user          |
| POST   | `/preferences/set-quiet-hours-for-user`         | Set quiet hours for a user                     |
| POST   | `/preferences/bulk-update-for-user`             | Bulk update all preferences for a user         |
| POST   | `/preferences/reset-to-defaults`                | Reset user preferences to defaults             |
| POST   | `/preferences/create-defaults-for-user`         | Create default preferences for a new user      |
| POST   | `/preferences/export-user-preferences`          | Export user preferences                        |
| POST   | `/preferences/import-user-preferences`          | Import user preferences                        |
| POST   | `/preferences/migrate-user-preferences`         | Migrate preferences between versions           |

#### Attempts

| Method | Endpoint                                        | Description                                   |
|--------|-------------------------------------------------|-----------------------------------------------|
| GET    | `/attempts`                                     | List all delivery attempts                     |
| POST   | `/attempts`                                     | Create an attempt record                       |
| GET    | `/attempts/{id}`                                | Get a single attempt                           |
| PUT    | `/attempts/{id}`                                | Update an attempt                              |
| DELETE | `/attempts/{id}`                                | Delete an attempt                              |
| GET    | `/attempts/stats`                               | Attempt statistics                             |
| GET    | `/attempts/pending`                             | List pending attempts                          |
| GET    | `/attempts/ready-for-retry`                     | List attempts ready for retry                  |
| GET    | `/attempts/failures`                            | List all failed attempts                       |
| GET    | `/attempts/recent-failures`                     | List recent failures                           |
| GET    | `/attempts/successful`                          | List successful attempts                       |
| GET    | `/attempts/channel/{channel}`                   | List attempts for a specific channel           |
| GET    | `/attempts/channel-stats`                       | Statistics per channel                         |
| GET    | `/attempts/success-rates`                       | Success rates by channel/type                  |
| GET    | `/attempts/error-codes`                         | List all error codes encountered               |
| GET    | `/attempts/average-retry-time`                  | Average time between retries                   |
| GET    | `/attempts/notification/{notificationId}`       | List attempts for a specific notification      |
| POST   | `/attempts/{id}/mark-processing`                | Mark attempt as processing                     |
| POST   | `/attempts/{id}/mark-success`                   | Mark attempt as successful                     |
| POST   | `/attempts/{id}/mark-failed`                    | Mark attempt as failed                         |
| POST   | `/attempts/{id}/mark-retry`                     | Mark attempt for retry                         |
| POST   | `/attempts/retry-failed`                        | Retry all failed attempts                      |
| POST   | `/attempts/clean-old`                           | Clean old attempt records                      |

### Filters

#### Notification Filters

| Filter Field            | Type   | Notes                                            |
|-------------------------|--------|--------------------------------------------------|
| `id`                    | number |                                                  |
| `notification_type_id`  | number |                                                  |
| `status`                | text   | `pending`, `sent`, `failed`, `partial`, `read`   |
| `priority`              | number | 1 (lowest) to 10 (highest)                      |
| `notifiable_type`       | text   | Polymorphic type (e.g., `Customers`, `Users`)    |
| `notifiable_id`         | number |                                                  |
| `creator_type`          | text   | Polymorphic type                                 |
| `creator_id`            | number |                                                  |
| `channels`              | text   | `email`, `database`, `broadcast`, `sms`, `push`, `slack` |

#### Notification Type Filters

| Filter Field            | Type       | Notes                                    |
|-------------------------|------------|------------------------------------------|
| `id`                    | number     |                                          |
| `name`                  | text       |                                          |
| `slug`                  | text       |                                          |
| `is_active`             | bool       |                                          |
| `is_user_configurable`  | bool       |                                          |
| `supported_channels`    | json_array | Array of channel strings                 |
| `scope_type`            | text       | `global`, `specific`                     |

#### Preference Filters

| Filter Field            | Type   | Notes                                            |
|-------------------------|--------|--------------------------------------------------|
| `id`                    | number |                                                  |
| `user_type`             | text   | Polymorphic type                                 |
| `user_id`               | number |                                                  |
| `notification_type_id`  | number |                                                  |
| `is_enabled`            | bool   |                                                  |
| `frequency`             | text   | `immediate`, `daily_digest`, `weekly_digest`, `disabled` |
| `channels`              | text   |                                                  |

#### Attempt Filters

| Filter Field                       | Type   | Notes                               |
|------------------------------------|--------|--------------------------------------|
| `id`                               | number |                                     |
| `notification_id`                  | number |                                     |
| `channel`                          | text   | `email`, `sms`, `push`, `slack`, `broadcast`, `database` |
| `status`                           | text   | `pending`, `processing`, `success`, `failed`, `retry` |
| `attempt_number`                   | number |                                     |
| `error_code`                       | text   |                                     |
| `attempted_at`                     | date   |                                     |
| `notification.notification_type_id`| number | Relation filter (notification)      |

### Includes

| Resource                | Available Includes                                            |
|-------------------------|---------------------------------------------------------------|
| **Notifications**       | `notificationType`, `notifiable`, `creator`, `attempts`       |
| **Notification Types**  | `notifications`                                               |
| **Preferences**         | `notificationType`, `user`                                    |
| **Attempts**            | `notification`, `notification.notificationType`               |

### Validation Rules

#### Create Notification — `POST /notifications`

| Field                 | Rules                                                       |
|-----------------------|-------------------------------------------------------------|
| `notification_type_id`| required, integer                                           |
| `notifiable_type`     | required, string                                            |
| `notifiable_id`       | required, integer                                           |
| `title`               | required, string, max: 255                                  |
| `message`             | required, string                                            |
| `channels`            | sometimes, array, each in: `email`, `database`, `broadcast`, `sms`, `push`, `slack` |
| `priority`            | sometimes, integer, min: 1, max: 10                         |
| `data`                | sometimes, array                                            |

#### Create Notification Type — `POST /types`

| Field                   | Rules                                                     |
|-------------------------|-----------------------------------------------------------|
| `name`                  | required, string, max: 255                                |
| `slug`                  | nullable, string, unique (MongoDB)                        |
| `supported_channels`    | sometimes, array, each in: `email`, `database`, `broadcast`, `sms`, `push`, `slack` |
| `default_channels`      | sometimes, array                                          |
| `is_active`             | sometimes, boolean                                        |
| `is_user_configurable`  | sometimes, boolean                                        |
| `scope_type`            | sometimes, in: `global`, `specific`                       |
| `role_codes`            | nullable, array                                           |

#### Create Preference — `POST /preferences`

| Field                   | Rules                                                     |
|-------------------------|-----------------------------------------------------------|
| `user_type`             | required, string                                          |
| `user_id`               | required, integer                                         |
| `notification_type_id`  | required, integer                                         |
| `channels`              | sometimes, array, each in: `email`, `database`, `broadcast`, `sms`, `push`, `slack` |
| `is_enabled`            | sometimes, boolean                                        |
| `frequency`             | sometimes, in: `immediate`, `daily_digest`, `weekly_digest`, `disabled` |
| `quiet_hours_start`     | nullable, string, regex: `HH:MM`                         |
| `quiet_hours_end`       | nullable, string, regex: `HH:MM`                         |
| `timezone`              | nullable, string (valid timezone)                         |
| `settings`              | sometimes, array                                          |

#### Create Attempt — `POST /attempts`

| Field              | Rules                                                        |
|--------------------|--------------------------------------------------------------|
| `notification_id`  | required, integer                                            |
| `channel`          | required, in: `email`, `database`, `broadcast`, `sms`, `push`, `slack` |
| `status`           | sometimes, in: `pending`, `processing`, `success`, `failed`, `retry` |
| `attempt_number`   | sometimes, integer, min: 1                                   |
| `error_code`       | nullable, string                                             |
| `error_message`    | nullable, string                                             |
| `attempted_at`     | nullable, date                                               |

### Examples

#### 1. List failed notifications with includes

```bash
curl -X GET \
  'https://example.com/api/v1/apps/notification-hub/notifications?filter[status]=[{"condition":"=","value":"failed"}]&include=notificationType,attempts,creator&per_page=20&sort=-_created_at' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Accept: application/json'
```

#### 2. Create a notification for a specific user

```bash
curl -X POST \
  'https://example.com/api/v1/apps/notification-hub/notifications/create-for-user' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "notification_type_id": 5,
    "notifiable_type": "Customers",
    "notifiable_id": 1042,
    "title": "Order Shipped",
    "message": "Your order #ORD-2024-8847 has been shipped and is on its way.",
    "channels": ["email", "database", "push"],
    "priority": 7,
    "data": {
      "order_id": 8847,
      "tracking_number": "1Z999AA10123456784",
      "carrier": "UPS"
    }
  }'
```

#### 3. Get dashboard overview

```bash
curl -X GET \
  'https://example.com/api/v1/apps/notification-hub/dashboard/overview' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Accept: application/json'
```

#### 4. Filter delivery attempts by channel

```bash
curl -X GET \
  'https://example.com/api/v1/apps/notification-hub/attempts?filter[channel]=[{"condition":"=","value":"email"}]&filter[status]=[{"condition":"IN","value":["failed","retry"]}]&include=notification,notification.notificationType&sort=-attempted_at&per_page=50' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Accept: application/json'
```

#### 5. Test a notification channel connection

```bash
curl -X POST \
  'https://example.com/api/v1/apps/notification-hub/settings/email/test' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "recipient": "admin@example.com",
    "subject": "Test Notification",
    "message": "This is a test notification to verify the email channel configuration."
  }'
```

---

## Appendix: Quick Reference

### All Hub Base URLs

| Hub              | Base URL                               |
|------------------|----------------------------------------|
| AttributesHub    | `api/v1/apps/attributes-hub/`          |
| CustomerHub      | `api/v1/apps/customer-hub/`            |
| LicenseHub       | `api/v1/apps/license-hub/`             |
| MediaHub         | `api/v1/apps/media-hub/`               |
| NotificationHub  | `api/v1/apps/notification-hub/`        |

### Supported Notification Channels

| Channel     | Description                         |
|-------------|-------------------------------------|
| `email`     | Email delivery                      |
| `database`  | In-app database storage             |
| `broadcast` | Real-time broadcasting (WebSocket)  |
| `sms`       | SMS text message                    |
| `push`      | Push notification                   |
| `slack`     | Slack message                       |

### Filter Condition Quick Reference

| Condition    | Usage                          | Value Required |
|--------------|--------------------------------|----------------|
| `=`          | Exact match                    | Yes            |
| `!=`         | Not equal                      | Yes            |
| `>`          | Greater than                   | Yes            |
| `<`          | Less than                      | Yes            |
| `>=`         | Greater than or equal          | Yes            |
| `<=`         | Less than or equal             | Yes            |
| `LIKE`       | Pattern match (`%` wildcards)  | Yes            |
| `IN`         | Value in array                 | Yes (array)    |
| `NOT IN`     | Value not in array             | Yes (array)    |
| `EMPTY`      | Field is null/empty            | No             |
| `NOT EMPTY`  | Field has a value              | No             |

---

> All list endpoints support Spatie QueryBuilder via `filter[field]=value`, `include=relation`, `sort=field`, and `page[number]=N&page[size]=N`.

---

## 6. OrderHub

**Base URL:** `api/v1/apps/order-hub/`

### Public Routes (No Authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/payment/webhook/{installationKey}/{provider}` | Payment provider webhook callback (Stripe, Mollie, etc.) |
| GET | `/order/payment/{installationKey}/{order_id}` | Payment redirect after checkout (success/failure landing) |

### Authenticated Endpoints

#### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/orders` | List all orders (paginated, filterable) |
| POST | `/orders` | Create a new order |
| GET | `/orders/{id}` | Get order details |
| PUT | `/orders/{id}` | Update an order |
| DELETE | `/orders/{id}` | Delete an order |
| GET | `/orders/statuses/list` | List all available order statuses |
| GET | `/orders/statuses/options` | Get order statuses as select options |
| POST | `/orders/statuses` | Create a custom order status |
| DELETE | `/orders/statuses/{status}` | Delete a custom order status |

#### Order Line Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/order-line-items` | List all order line items |
| POST | `/order-line-items` | Create a line item |
| GET | `/order-line-items/{id}` | Get line item details |
| PUT | `/order-line-items/{id}` | Update a line item |
| DELETE | `/order-line-items/{id}` | Delete a line item |

#### Order Comments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/order-comments` | List all order comments |
| POST | `/order-comments` | Add a comment to an order |
| GET | `/order-comments/{id}` | Get comment details |
| PUT | `/order-comments/{id}` | Update a comment |
| DELETE | `/order-comments/{id}` | Delete a comment |

#### Carts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/carts` | List all carts |
| POST | `/carts` | Create a new cart |
| GET | `/carts/{id}` | Get cart details |
| PUT | `/carts/{id}` | Update a cart |
| PATCH | `/carts` | Upsert cart by `session_uuid` (creates or updates) |
| DELETE | `/carts/{id}` | Delete a cart |

#### Cart Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/cart-items` | List all cart items |
| POST | `/cart-items` | Add item to cart |
| GET | `/cart-items/{id}` | Get cart item details |
| PUT | `/cart-items/{id}` | Update cart item |
| DELETE | `/cart-items/{id}` | Remove item from cart |

#### Checkout

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/carts/{cart}/checkout` | Preview checkout (calculate totals, shipping, tax) |
| POST | `/carts/{cart}/checkout` | Complete checkout — converts cart to order |

#### Billing Methods

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/billing-methods` | List all billing methods |
| POST | `/billing-methods` | Create a billing method |
| GET | `/billing-methods/{id}` | Get billing method details |
| PUT | `/billing-methods/{id}` | Update a billing method |
| DELETE | `/billing-methods/{id}` | Delete a billing method |
| GET | `/billing-methods/payment-providers/templates` | List available payment provider templates |
| POST | `/billing-methods/payment-providers/templates` | Create a billing method from provider template |

#### Shipping Methods

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/shipping-methods` | List all shipping methods |
| POST | `/shipping-methods` | Create a shipping method |
| GET | `/shipping-methods/{id}` | Get shipping method details |
| PUT | `/shipping-methods/{id}` | Update a shipping method |
| DELETE | `/shipping-methods/{id}` | Delete a shipping method |

#### Customer Payment Methods

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/customer-payment-methods` | List customer payment methods |
| POST | `/customer-payment-methods` | Add a customer payment method |
| GET | `/customer-payment-methods/{id}` | Get payment method details |
| PUT | `/customer-payment-methods/{id}` | Update a payment method |
| DELETE | `/customer-payment-methods/{id}` | Remove a payment method |

#### Quotes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/quotes` | List all quotes |
| POST | `/quotes` | Create a new quote |
| GET | `/quotes/{id}` | Get quote details |
| PUT | `/quotes/{id}` | Update a quote |
| DELETE | `/quotes/{id}` | Delete a quote |

#### Quote Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/quote-items` | List all quote items |
| POST | `/quote-items` | Add item to a quote |
| GET | `/quote-items/{id}` | Get quote item details |
| PUT | `/quote-items/{id}` | Update a quote item |
| DELETE | `/quote-items/{id}` | Remove a quote item |

#### Quote Item Groups

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/quote-items-groups` | List all quote item groups |
| POST | `/quote-items-groups` | Create a quote item group |
| GET | `/quote-items-groups/{id}` | Get group details |
| PUT | `/quote-items-groups/{id}` | Update a group |
| DELETE | `/quote-items-groups/{id}` | Delete a group |

### Filters

#### Order Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact order ID |
| `status` | text | Order status (draft, pending, invoiced, shipped, completed, pending_payment, paid, refunded, partially_refunded, canceled, processing) |
| `total_price` | number | Total order price (supports `gt`, `lt`, `gte`, `lte`) |
| `customer_id` | number | Filter by customer |
| `shipping_method_id` | number | Filter by shipping method |
| `billing_method_id` | number | Filter by billing method |
| `external_id` | text | External system reference ID |
| `order_number` | text | Human-readable order number |
| `_created_at` | date | Creation date (ISO 8601, supports range) |
| `_updated_at` | date | Last update date (ISO 8601, supports range) |

#### Cart Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact cart ID |
| `session_uuid` | text | Session identifier for guest carts |
| `total_price` | number | Total cart value |
| `customer_id` | number | Filter by customer |
| `_created_at` | date | Creation date |
| `_updated_at` | date | Last update date |

#### Order Line Item Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact line item ID |
| `name` | text | Line item name (partial match) |
| `order_id` | number | Parent order ID |
| `quantity` | number | Quantity |
| `price` | number | Unit price |
| `total_price` | number | Line total |
| `product_id` | number | Associated product ID |
| `_created_at` | date | Creation date |
| `_updated_at` | date | Last update date |

#### Cart Item Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact cart item ID |
| `cart_id` | number | Parent cart ID |
| `product_id` | number | Product ID |
| `quantity` | number | Quantity in cart |
| `price` | number | Unit price |

#### Order Comment Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact comment ID |
| `comment` | text | Comment body (partial match) |
| `order_id` | number | Parent order ID |
| `_created_at` | date | Creation date |
| `_updated_at` | date | Last update date |

#### Billing Method Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact billing method ID |
| `name` | text | Billing method name |
| `_created_at` | date | Creation date |
| `_updated_at` | date | Last update date |

#### Shipping Method Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact shipping method ID |
| `name` | text | Shipping method name |
| `_created_at` | date | Creation date |
| `_updated_at` | date | Last update date |

#### Customer Payment Method Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact payment method ID |
| `provider` | text | Payment provider (stripe, mollie, etc.) |
| `brand` | text | Card brand (visa, mastercard, etc.) |
| `_created_at` | date | Creation date |
| `_updated_at` | date | Last update date |

#### Quote Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact quote ID |
| `total_price` | number | Quote total |
| `customer_id` | number | Customer ID |
| `_created_at` | date | Creation date |
| `_updated_at` | date | Last update date |

#### Quote Item Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact quote item ID |
| `quote_id` | number | Parent quote ID |
| `order_id` | number | Linked order ID (if converted) |
| `product_id` | number | Product ID |
| `group_id` | number | Quote item group ID |
| `quantity` | number | Quantity |
| `price` | number | Unit price |

#### Quote Item Group Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact group ID |
| `name` | text | Group name |
| `quote_id` | number | Parent quote ID |
| `_created_at` | date | Creation date |
| `_updated_at` | date | Last update date |

### Includes

#### Order Includes

| Include | Description |
|---------|-------------|
| `customer` | Customer who placed the order |
| `customer.company` | Customer's company details |
| `shippingMethod` | Shipping method used |
| `billingMethod` | Billing/payment method used |
| `orderLineItems` | All line items in the order |
| `comments` | Order comments/notes |
| `orderLineItems.product` | Product details for each line item |
| `orderLineItems.product.mainMedia` | Primary product image per line item |
| `orderLineItems.product.media` | All product media per line item |
| `shippingAddress` | Shipping address |
| `billingAddress` | Billing address |
| `attributeValues` | Custom attribute values on the order |
| `attributeValues.value` | The attribute value object |
| `attributeValues.value.translation` | Translated attribute value |
| `attributeValues.value.attribute` | Parent attribute definition |

#### Cart Includes

| Include | Description |
|---------|-------------|
| `session` | Session data for guest carts |
| `cartItems` | All items in the cart |
| `cartItems.product` | Product for each cart item |
| `cartItems.product.productImages` | Product images |
| `cartItems.product.prices` | All prices for the product |
| `cartItems.product.price` | Regular price |
| `cartItems.product.specialPrice` | Special/sale price |
| `cartItems.product.finalPrice` | Computed final price |
| `cartItems.product.tierPrices` | Tier pricing tiers |
| `cartItems.product.finalTierPrices` | Computed tier prices |
| `cartItems.product.groupPrices` | Customer group prices |
| `cartItems.product.media` | All product media |
| `cartItems.product.mainMedia` | Primary product image |
| `cartItems.product.crossSells` | Cross-sell products |
| `cartItems.product.upSells` | Up-sell products |
| `customer` | Cart owner (if authenticated) |
| `customer.company` | Cart owner's company |

#### Order Line Item Includes

| Include | Description |
|---------|-------------|
| `order` | Parent order |
| `product` | Associated product |

#### Cart Item Includes

| Include | Description |
|---------|-------------|
| `cart` | Parent cart |
| `product` | Associated product |
| `product.mainMedia` | Product primary image |
| `product.crossSells.crossSellProduct.mainMedia` | Cross-sell product images |
| `product.upSells.upSellProduct.mainMedia` | Up-sell product images |

#### Order Comment Includes

| Include | Description |
|---------|-------------|
| `order` | Parent order |

#### Billing Method Includes

| Include | Description |
|---------|-------------|
| `order` | Associated order |

#### Shipping Method Includes

| Include | Description |
|---------|-------------|
| `order` | Associated order |

#### Customer Payment Method Includes

| Include | Description |
|---------|-------------|
| `billingMethod` | Linked billing method configuration |

#### Quote Includes

| Include | Description |
|---------|-------------|
| `quoteItems` | All items in the quote |
| `quoteItems.product` | Product for each quote item |
| `quoteItems.product.prices` | Product prices |
| `quoteItems.product.media` | Product media |
| `customer` | Quote customer |
| `customer.company` | Customer company details |

#### Quote Item Includes

| Include | Description |
|---------|-------------|
| `quote` | Parent quote |
| `quote.customer` | Quote's customer |
| `order` | Linked order (if converted) |
| `order.orderItems` | Order line items (if converted) |
| `product` | Associated product |
| `product.prices` | Product pricing |
| `product.media` | Product media |

#### Quote Item Group Includes

| Include | Description |
|---------|-------------|
| `quoteItems` | Items in this group |
| `quoteItems.product` | Product per group item |
| `quote` | Parent quote |
| `quote.customer` | Quote customer |
| `quote.customer.company` | Customer company |

### Validation Rules

#### Create Order

| Field | Rules |
|-------|-------|
| `status` | required · in:draft,pending,invoiced,shipped,completed,pending_payment,paid,refunded,partially_refunded,canceled,processing |
| `customer_id` | required · numeric |
| `shipping_method_id` | numeric |
| `billing_method_id` | numeric |
| `shipping_address_id` | numeric |
| `billing_address_id` | numeric |
| `external_id` | sometimes · nullable · unique (across orders) |
| `order_number` | sometimes · nullable · unique (across orders) |
| `line_items` | required · array · min:1 |
| `line_items.*.name` | required · string |
| `line_items.*.quantity` | required · numeric |
| `line_items.*.price` | required · numeric |
| `line_items.*.product_id` | numeric (optional link to ProductHub product) |
| `attributes` | array · nullable (custom attribute values) |

#### Create Cart

| Field | Rules |
|-------|-------|
| `is_active` | sometimes · boolean |
| `session_uuid` | sometimes · nullable (for guest cart identification) |
| `customer_id` | sometimes · nullable · numeric |
| `cart_items` | required · array · min:1 |
| `cart_items.*.quantity` | required · numeric |
| `cart_items.*.product_id` | numeric |

#### Checkout

| Field | Rules |
|-------|-------|
| `shipping_method_id` | required · numeric |
| `billing_method_id` | required · numeric |
| `shipping_address_id` | required · numeric |
| `billing_address_id` | required · numeric |
| `comment` | string (optional order comment) |

### Examples

#### 6.1 — List Orders with Includes

```bash
curl -s -X GET \
  'https://api.datahub.syncspider.com/api/v1/apps/order-hub/orders?include=customer,customer.company,orderLineItems,orderLineItems.product.mainMedia,shippingMethod,billingMethod,shippingAddress,billingAddress&page[size]=20&sort=-_created_at' \
  -H 'Authorization: Bearer {token}' \
  -H 'Accept: application/json'
```

#### 6.2 — Filter Orders by Status and Date Range

```bash
curl -s -X GET \
  'https://api.datahub.syncspider.com/api/v1/apps/order-hub/orders?filter[status]=pending,processing&filter[_created_at]=2024-01-01,2024-12-31&include=customer,orderLineItems&sort=-total_price' \
  -H 'Authorization: Bearer {token}' \
  -H 'Accept: application/json'
```

#### 6.3 — Create an Order with Line Items

```bash
curl -s -X POST \
  'https://api.datahub.syncspider.com/api/v1/apps/order-hub/orders' \
  -H 'Authorization: Bearer {token}' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "status": "pending",
    "customer_id": 42,
    "shipping_method_id": 1,
    "billing_method_id": 2,
    "shipping_address_id": 15,
    "billing_address_id": 15,
    "external_id": "ERP-2024-00891",
    "line_items": [
      {
        "name": "Premium Widget",
        "quantity": 3,
        "price": 29.99,
        "product_id": 105
      },
      {
        "name": "Widget Accessory Pack",
        "quantity": 1,
        "price": 14.50,
        "product_id": 210
      }
    ],
    "attributes": [
      {"attribute_id": 5, "value": "Express handling requested"}
    ]
  }'
```

#### 6.4 — Upsert Cart by Session UUID

```bash
curl -s -X PATCH \
  'https://api.datahub.syncspider.com/api/v1/apps/order-hub/carts' \
  -H 'Authorization: Bearer {token}' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "session_uuid": "a3f8c912-7b4e-4d1a-9c6e-2f8b1d0e5a73",
    "is_active": true,
    "cart_items": [
      {"product_id": 105, "quantity": 2},
      {"product_id": 210, "quantity": 1}
    ]
  }'
```

#### 6.5 — Complete Checkout

```bash
curl -s -X POST \
  'https://api.datahub.syncspider.com/api/v1/apps/order-hub/carts/17/checkout' \
  -H 'Authorization: Bearer {token}' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "shipping_method_id": 1,
    "billing_method_id": 2,
    "shipping_address_id": 15,
    "billing_address_id": 15,
    "comment": "Please gift-wrap the order."
  }'
```

#### 6.6 — Filter Orders by Customer

```bash
curl -s -X GET \
  'https://api.datahub.syncspider.com/api/v1/apps/order-hub/orders?filter[customer_id]=42&include=customer,orderLineItems,comments&sort=-_created_at&page[size]=10' \
  -H 'Authorization: Bearer {token}' \
  -H 'Accept: application/json'
```

---

## 7. ProductHub ⭐ (Most Complex Hub)

**Base URL:** `api/v1/apps/product-hub/`

ProductHub is the most feature-rich hub in the DataHub platform. It manages products with complex pricing (regular, special, tier, group, cost), multi-warehouse stock, configurable/variation products, category trees with anchor categories, media management, cross-sells/up-sells, vendor relationships, AI-generated descriptions, translations, and deep attribute filtering.

### Endpoints

#### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products` | List all products (paginated, 26 filters, 42+ includes) |
| POST | `/products` | Create a new product |
| GET | `/products/{id}` | Get product details |
| PUT | `/products/{id}` | Update a product |
| DELETE | `/products/{id}` | Delete a product |
| PUT | `/products/upsert/single` | Create or update a product by SKU (idempotent) |
| PUT | `/products/bulk/update` | Bulk update multiple products |
| DELETE | `/products/bulk/delete` | Bulk delete multiple products |
| PUT | `/products/{id}/createVariations` | Generate child variation products from attributes |
| PUT | `/products/{id}/attachVariationsAttributes` | Attach variation attributes to a configurable product |
| DELETE | `/products/{parentId}/child-products` | Remove child products from a parent |
| PUT | `/products/{id}/generateAIDescription` | Generate AI-powered product description |

#### Categories

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/categories` | List all categories (tree-structured) |
| POST | `/categories` | Create a category |
| GET | `/categories/{id}` | Get category details |
| PUT | `/categories/{id}` | Update a category |
| DELETE | `/categories/{id}` | Delete a category |
| GET | `/categories/by-path/find` | Find category by URL path/slug |
| POST | `/categories/update/depths` | Recalculate category tree depths |

#### Stock

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/stock` | List all stock records |
| POST | `/stock` | Create a stock record |
| GET | `/stock/{id}` | Get stock details |
| PUT | `/stock/{id}` | Update a stock record |
| DELETE | `/stock/{id}` | Delete a stock record |
| POST | `/stock/upsert/bulk` | Bulk upsert stock records |

#### Prices

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/prices` | List all price records |
| POST | `/prices` | Create a price record |
| GET | `/prices/{id}` | Get price details |
| PUT | `/prices/{id}` | Update a price record |
| DELETE | `/prices/{id}` | Delete a price record |
| POST | `/prices/upsert/bulk` | Bulk upsert price records |

#### Warehouses

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/warehouses` | List all warehouses |
| POST | `/warehouses` | Create a warehouse |
| GET | `/warehouses/{id}` | Get warehouse details |
| PUT | `/warehouses/{id}` | Update a warehouse |
| DELETE | `/warehouses/{id}` | Delete a warehouse |

#### Media

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/media` | List all media |
| POST | `/media` | Upload media |
| GET | `/media/{id}` | Get media details |
| PUT | `/media/{id}` | Update media metadata |
| DELETE | `/media/{id}` | Delete media |

#### Vendors

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/vendors` | List all vendors |
| POST | `/vendors` | Create a vendor |
| GET | `/vendors/{id}` | Get vendor details |
| PUT | `/vendors/{id}` | Update a vendor |
| DELETE | `/vendors/{id}` | Delete a vendor |

#### Translations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/translations` | List all translations |
| POST | `/translations` | Create a translation |
| GET | `/translations/{id}` | Get translation details |
| PUT | `/translations/{id}` | Update a translation |
| DELETE | `/translations/{id}` | Delete a translation |
| PUT | `/translations/upsert/single` | Upsert a single translation |
| PUT | `/translations/upsert/bulk` | Bulk upsert translations |
| POST | `/translations/job/run` | Trigger AI translation job |
| GET | `/translations/job/progress` | Check translation job progress |

#### Demo Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/demoData/deploy` | Deploy demo product catalog |

#### Attributes / Attribute Values / Attribute Groups

Same endpoints as AttributesHub — full CRUD on `/attributes`, `/attribute-values`, `/attribute-groups`.

#### Customer Groups

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/customer/groups` | List customer groups |
| POST | `/customer/groups` | Create a customer group |
| GET | `/customer/groups/{id}` | Get group details |
| PUT | `/customer/groups/{id}` | Update a group |
| DELETE | `/customer/groups/{id}` | Delete a group |

### Product Filters (26 Filters — Complete Reference)

ProductHub supports the most extensive filter set in the platform. Filters are applied via `filter[key]=value` query parameters.

#### Standard Filters

| # | Filter Key | Type | Description |
|---|------------|------|-------------|
| 1 | `id` | number | Exact product ID or comma-separated list |
| 2 | `name` | text | Product name (partial match supported) |
| 3 | `sku` | text | Product SKU (exact or partial match) |
| 4 | `status` | text | Product status: `draft`, `private`, `public` |
| 5 | `product_type` | text | Product type: `simple`, `configurable`, `license`, `dt-one` |
| 6 | `seo_slug` | text | SEO-friendly URL slug |
| 7 | `_created_at` | date | Creation date (ISO 8601, supports range with comma) |
| 8 | `_updated_at` | date | Last update date (ISO 8601, supports range) |

#### Relation Filters (through related collections)

| # | Filter Key | Type | Description |
|---|------------|------|-------------|
| 9 | `stock.warehouse_id` | number | Filter by warehouse via stock relation |
| 10 | `stock.stock_quantity` | number | Filter by stock quantity via stock relation |
| 11 | `defaultStock.stock_quantity` | number | Filter by default warehouse stock quantity |
| 12 | `price` | number | Filter by regular price (supports range) |
| 13 | `specialPrice` | number | Filter by special/sale price |
| 14 | `finalPrice` | number | Filter by computed final price |
| 15 | `attributeValues.value.attribute_id` | number | Filter by attribute definition ID |
| 16 | `attributeValues.value.attribute_value` | text | Filter by attribute value text |
| 17 | `attributeValues.attribute_value_id` | number | Filter by specific attribute value ID |
| 18 | `categories.category_id` | number | Filter by exact category (no descendants) |

#### Special Callback Filters

These filters use custom callback logic and have special behavior:

| # | Filter Key | Type | Description |
|---|------------|------|-------------|
| 19 | `attribute` | JSON array | **Advanced attribute filtering** via `AttributeFilterRepository`. Accepts a JSON array of conditions. See format below. |
| 20 | `exclude_child_products` | callback | Set to `1` to exclude products that have a parent (child variations). Returns only standalone and parent products. |
| 21 | `exclude_parent_products` | callback | Set to `1` to exclude configurable parent products. Returns only simple/child products. |
| 22 | `without_stock` | callback | Set to `1` to exclude products that have no stock records at all. |
| 23 | `exclude_child_products_id` | callback | Provide a parent product ID to exclude all children of that specific parent. |
| 24 | `parent_id` | callback | Provide a parent product ID to return only its direct child products (variations). |
| 25 | `search` | callback | **Full-text search** across `name`, `sku`, `description`, and `short_description` fields simultaneously. |
| 26 | `anchor_category_id` | callback | Filter by category **and all its descendant categories**. Unlike `categories.category_id` which is exact, this traverses the entire category subtree. |

#### Attribute Filter Format (Filter #19)

The `attribute` filter uses the `AttributeFilterRepository` and accepts a JSON-encoded array:

```
filter[attribute]=[{"attribute_id":1,"attribute_value":"Red","condition":"IN","operator":"AND"},{"attribute_id":3,"attribute_value":"Large,Medium","condition":"IN","operator":"AND"}]
```

**Fields:**

| Field | Values | Description |
|-------|--------|-------------|
| `attribute_id` | number | The attribute definition ID |
| `attribute_value` | string | Value(s) to match — comma-separated for multi-value |
| `condition` | `IN`, `NOT_IN`, `EQUALS`, `NOT_EQUALS`, `LIKE`, `GT`, `LT`, `GTE`, `LTE` | Match condition |
| `operator` | `AND`, `OR` | How to combine with other attribute conditions |

**Examples:**

- Products with Color=Red AND Size=Large:
  ```
  [{"attribute_id":1,"attribute_value":"Red","condition":"IN","operator":"AND"},{"attribute_id":2,"attribute_value":"Large","condition":"IN","operator":"AND"}]
  ```
- Products with Color=Red OR Color=Blue:
  ```
  [{"attribute_id":1,"attribute_value":"Red,Blue","condition":"IN","operator":"OR"}]
  ```
- Products NOT in Material=Plastic:
  ```
  [{"attribute_id":5,"attribute_value":"Plastic","condition":"NOT_IN","operator":"AND"}]
  ```

### Product Includes (42+ Includes — Complete Reference)

ProductHub offers the deepest include graph. Use includes judiciously to avoid performance issues on large catalogs.

#### Stock Includes

| Include | Description |
|---------|-------------|
| `stock` | All stock records across all warehouses |
| `stock.warehouse` | Warehouse details per stock record |
| `stockLocations` | Stock by location (shelf, bin, etc.) |
| `stockLocations.warehouse` | Warehouse for each stock location |

#### Pricing Includes

| Include | Description |
|---------|-------------|
| `prices` | All price records (regular, special, tier, group, cost) |
| `price` | Regular price only |
| `specialPrice` | Special/sale price only |
| `finalPrice` | Computed final price (considers special price, date ranges) |
| `costPrice` | Cost/wholesale price |
| `tierPrices` | Tier pricing tiers (quantity-based discounts) |
| `finalTierPrices` | Computed final tier prices |
| `groupPrices` | Customer group-specific prices |

#### Attribute Includes

| Include | Description |
|---------|-------------|
| `attributeValues` | All attribute values assigned to the product |
| `attributeValues.value` | The attribute value object |
| `attributeValues.value.translation` | Translated attribute value label |
| `attributeValues.value.attribute.translation` | Translated attribute name |
| `attributeValues.value.attribute.group` | Attribute group the attribute belongs to |

#### Media Includes

| Include | Description |
|---------|-------------|
| `media` | All media (images, videos, documents) |
| `mainMedia` | Primary/featured media item |

#### Cross-Sell & Up-Sell Includes

| Include | Description |
|---------|-------------|
| `crossSells` | Cross-sell relationship records |
| `crossSells.product` | The source product in cross-sell |
| `crossSells.crossSellProduct` | The cross-sell target product (with nested prices, media, mainMedia) |
| `upSells` | Up-sell relationship records |
| `upSells.product` | The source product in up-sell |
| `upSells.upSellProduct` | The up-sell target product (with nested prices, media, mainMedia) |

#### Vendor Includes

| Include | Description |
|---------|-------------|
| `vendorProduct` | Vendor-product relationship |
| `vendorProduct.vendor` | Vendor details |

#### Variation / Configurable Product Includes

| Include | Description |
|---------|-------------|
| `parentProductAttributes` | Attributes that define variations on parent |
| `parentProductAttributes.product` | Parent product from attribute relation |
| `parentProductAttributes.attribute` | The attribute used for variation |
| `childProducts` | Direct child variation records |
| `childProducts.childProduct` | Full child product (with all nested: prices, stock, media, attributes) |
| `parentProducts` | Parent product records (if this is a child) |

#### Category & Translation Includes

| Include | Description |
|---------|-------------|
| `categories` | Category assignment records |
| `categories.category` | Full category objects |
| `translation` | Product translations |

#### License Includes

| Include | Description |
|---------|-------------|
| `licenseConfiguration` | License generation configuration (for `license` type products) |

#### Custom Computed Includes

These are special includes that trigger custom logic, not simple relation loading:

| Include | Description |
|---------|-------------|
| `attributes` | **(Custom)** Returns a denormalized attribute summary — grouped attribute values with labels |
| `stockSum` | **(Custom)** Aggregated total stock quantity across all warehouses |
| `variationAttributes` | **(Custom)** For configurable parents: returns the variation-defining attributes and their available values across all children |

### Category Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact category ID |
| `name` | text | Category name |
| `slug` | text | URL slug |
| `parent_id` | number | Parent category ID (null for root) |
| `depth` | number | Tree depth level (0 = root) |
| `exclude_from_main_menu` | callback | Set to `1` to exclude categories hidden from main menu |
| `exclude_from_layer_navigation` | callback | Set to `1` to exclude categories hidden from layered navigation |

### Category Includes

| Include | Description |
|---------|-------------|
| `translation` | Category translations |
| `attributeValues` | Attribute values on the category (with nested value/translation/attribute) |
| `media` | All category media |
| `mainMedia` | Primary category image |
| `productsCount` | **(Custom)** Count of products in this category |

### Stock Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact stock record ID |
| `product_id` | number | Filter by product |
| `warehouse_id` | number | Filter by warehouse |
| `stock_quantity` | number | Stock quantity (supports range) |
| `product.name` | text | Filter via product name (relation filter) |
| `product.sku` | text | Filter via product SKU (relation filter) |
| `_created_at` | date | Creation date |
| `_updated_at` | date | Last update date |

### Stock Includes

| Include | Description |
|---------|-------------|
| `product` | Associated product |
| `translation` | Stock record translations |
| `warehouse` | Warehouse details |

### Price Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact price record ID |
| `product_id` | number | Filter by product |
| `customer_group_id` | number | Filter by customer group |
| `price_type` | text | Type: `regular`, `special`, `tier`, `group`, `cost` |
| `price` | number | Price amount (supports range) |
| `min_quantity` | number | Minimum quantity for tier pricing |
| `group` | text | Group identifier |
| `start_date` | date | Price validity start date |
| `end_date` | date | Price validity end date |
| `_created_at` | date | Creation date |
| `_updated_at` | date | Last update date |

### Price Includes

| Include | Description |
|---------|-------------|
| `product` | Associated product |
| `translation` | Price record translations |
| `customerGroup` | Customer group for group pricing |

### Vendor Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact vendor ID |
| `name` | text | Vendor name |
| `phone` | text | Phone number |
| `email` | text | Email address |
| `address` | text | Address |
| `_created_at` | date | Creation date |

### Vendor Includes

| Include | Description |
|---------|-------------|
| `vendorProducts` | Products supplied by this vendor |
| `translation` | Vendor translations |

### Media Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact media ID |
| `mediable_id` | number | Owner entity ID (product, category) |
| `media_type` | text | Type: image, video, document, etc. |
| `media_url` | text | Media URL |
| `alt_text` | text | Alt text |
| `is_primary` | boolean | Primary/featured flag |
| `_created_at` | date | Creation date |
| `_updated_at` | date | Last update date |

### Media Includes

| Include | Description |
|---------|-------------|
| `translation` | Media translations (alt text, titles per locale) |

### Validation Rules

#### Create / Upsert Product (Complete Reference)

This is the most complex validation in the platform. The upsert endpoint (`PUT /products/upsert/single`) uses the same rules with an additional `action` field.

**Top-Level Fields:**

| Field | Rules | Notes |
|-------|-------|-------|
| `action` | nullable · in:createOrUpdate,onlyCreate,onlyUpdate | Upsert endpoint only. Controls create vs update behavior |
| `name` | nullable · string · min:2 | Product name |
| `sku` | nullable · string · max:255 · min:2 · unique | Stock Keeping Unit — must be unique across all products |
| `product_type` | nullable · in:simple,configurable,license,dt-one | Cannot be changed after creation |
| `description` | nullable · string | Full HTML description |
| `short_description` | nullable · string | Brief description for listings |
| `status` | nullable · in:draft,private,public | Visibility status |
| `visibility` | nullable · in:search_catalog,search,catalog,hidden | Where the product appears |
| `tax_class_id` | nullable · numeric | Link to TaxHub tax class |
| `seo` | sometimes · array | SEO metadata (slug, meta_title, meta_description) |

**Stock (nested array):**

| Field | Rules |
|-------|-------|
| `stock` | array |
| `stock.*.warehouse_id` | numeric |
| `stock.*.stock_quantity` | numeric |

**Prices (nested object):**

| Field | Rules |
|-------|-------|
| `prices` | array |
| `prices.price` | numeric (regular price) |
| `prices.cost_price` | numeric (cost/wholesale) |
| `prices.special_price` | numeric (sale price) |
| `prices.special_price_start_date` | date · nullable |
| `prices.special_price_end_date` | date · nullable |
| `prices.group_prices` | array of {customer_group_id, price} |
| `prices.tier_prices` | array of {min_quantity, price} |

**Attributes (nested array):**

| Field | Rules |
|-------|-------|
| `attributes` | array |
| `attributes.*.attribute_id` | numeric (reference to attribute definition) |
| `attributes.*.value` | string (the attribute value) |
| `attributes.*.auto_create_value` | boolean (create value if it doesn't exist) |
| `attributes.*.is_variation_attribute` | boolean (marks as variation-defining for configurable products) |

**Media (nested array):**

| Field | Rules |
|-------|-------|
| `media` | array |
| `media.*.file` | file upload (binary) |
| `media.*.media_type` | string (image, video, document) |
| `media.*.media_url` | string (URL for external media) |
| `media.*.alt_text` | string |
| `media.*.is_primary` | boolean |
| `media.*.order` | numeric (display order) |

**Relations (arrays of IDs or objects):**

| Field | Rules |
|-------|-------|
| `child_products` | array (product IDs or objects for variations) |
| `parent_products` | array (parent product IDs) |
| `categories` | array (category IDs) |
| `cross_sells` | array (product IDs) |
| `up_sells` | array (product IDs) |

**License Configuration (for `license` type products):**

| Field | Rules |
|-------|-------|
| `license_configuration` | sometimes · array |
| `license_configuration.template` | string (license key template pattern) |
| `license_configuration.mode` | string (generation mode) |
| `license_configuration.allowed_chars` | string (character set for generation) |
| `license_configuration.auto_generate` | boolean |
| `license_configuration.quantity_per_order` | numeric |

#### Create Stock

| Field | Rules |
|-------|-------|
| `product_id` | required · numeric |
| `warehouse_id` | required · numeric |
| `stock_quantity` | required · numeric |
| `stock_availability` | required · boolean |
| `upcoming_qty` | array (future stock arrivals) |
| `backorders` | in:no_backorders,allow_qty_below_0,allow_pre_orders |

#### Create Price

| Field | Rules |
|-------|-------|
| `product_id` | required · numeric |
| `price_type` | required · in:regular,special,tier,group,cost |
| `price` | required · numeric |
| `min_quantity` | numeric · nullable · required_if:price_type,tier |
| `customer_group_id` | numeric · nullable · required_if:price_type,group |
| `start_date` | date · nullable |
| `end_date` | date · nullable |

#### Bulk Upsert Stock (`POST /stock/upsert/bulk`)

Request body is an array of stock objects:

| Field | Rules |
|-------|-------|
| `*.id` | sometimes (if updating existing record) |
| `*.product_id` | required_without:id |
| `*.warehouse_id` | required_without:id |
| `*.stock_quantity` | required |
| `*.stock_availability` | sometimes · boolean |
| `*.backorders` | sometimes · in:no_backorders,allow_qty_below_0,allow_pre_orders |

#### Bulk Upsert Prices (`POST /prices/upsert/bulk`)

Request body is an array of price objects:

| Field | Rules |
|-------|-------|
| `*.product_id` | required |
| `*.price_type` | required · in:regular,special,tier,group,cost |
| `*.price` | required · numeric |
| `*.min_quantity` | nullable |
| `*.customer_group_id` | nullable |
| `*.start_date` | nullable · date |
| `*.end_date` | nullable · date |

### Examples (10 curl Examples)

#### 7.1 — List Products with Prices and Stock

```bash
curl -s -X GET \
  'https://api.datahub.syncspider.com/api/v1/apps/product-hub/products?include=price,specialPrice,finalPrice,stock,stock.warehouse,mainMedia,categories.category&filter[status]=public&filter[exclude_child_products]=1&page[size]=25&sort=-_created_at' \
  -H 'Authorization: Bearer {token}' \
  -H 'Accept: application/json'
```

#### 7.2 — Full-Text Search Products

```bash
curl -s -X GET \
  'https://api.datahub.syncspider.com/api/v1/apps/product-hub/products?filter[search]=wireless+bluetooth+headphones&include=price,finalPrice,mainMedia,stockSum&filter[status]=public&filter[exclude_child_products]=1&page[size]=20' \
  -H 'Authorization: Bearer {token}' \
  -H 'Accept: application/json'
```

#### 7.3 — Filter by Anchor Category (Category + All Descendants)

```bash
# Category 5 is "Electronics" — anchor_category_id returns products in
# Electronics AND all subcategories (Phones, Laptops, Accessories, etc.)
curl -s -X GET \
  'https://api.datahub.syncspider.com/api/v1/apps/product-hub/products?filter[anchor_category_id]=5&include=price,finalPrice,mainMedia,categories.category&filter[status]=public&sort=name&page[size]=50' \
  -H 'Authorization: Bearer {token}' \
  -H 'Accept: application/json'
```

#### 7.4 — Filter by Attributes (AttributeFilterRepository Format)

```bash
# Find public products where Color is Red or Blue AND Size is Large
curl -s -X GET \
  'https://api.datahub.syncspider.com/api/v1/apps/product-hub/products?filter[attribute]=[{"attribute_id":1,"attribute_value":"Red,Blue","condition":"IN","operator":"AND"},{"attribute_id":2,"attribute_value":"Large","condition":"IN","operator":"AND"}]&filter[status]=public&include=attributeValues.value.translation,price,mainMedia' \
  -H 'Authorization: Bearer {token}' \
  -H 'Accept: application/json'
```

#### 7.5 — Filter by Price Range

```bash
# Products with final price between 10.00 and 99.99
curl -s -X GET \
  'https://api.datahub.syncspider.com/api/v1/apps/product-hub/products?filter[finalPrice]=10,99.99&include=price,specialPrice,finalPrice,mainMedia&filter[status]=public&sort=finalPrice' \
  -H 'Authorization: Bearer {token}' \
  -H 'Accept: application/json'
```

#### 7.6 — Create a Complete Product (Stock, Prices, Attributes, Media, Categories)

```bash
curl -s -X POST \
  'https://api.datahub.syncspider.com/api/v1/apps/product-hub/products' \
  -H 'Authorization: Bearer {token}' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "name": "Premium Wireless Headphones",
    "sku": "AUDIO-WH-PRO-001",
    "product_type": "simple",
    "description": "<p>High-fidelity wireless headphones with active noise cancellation, 40-hour battery life, and premium comfort padding.</p>",
    "short_description": "Premium ANC wireless headphones",
    "status": "public",
    "visibility": "search_catalog",
    "tax_class_id": 1,
    "stock": [
      {"warehouse_id": 1, "stock_quantity": 150},
      {"warehouse_id": 2, "stock_quantity": 75}
    ],
    "prices": {
      "price": 199.99,
      "cost_price": 89.00,
      "special_price": 169.99,
      "special_price_start_date": "2024-11-01",
      "special_price_end_date": "2024-12-31",
      "tier_prices": [
        {"min_quantity": 5, "price": 159.99},
        {"min_quantity": 10, "price": 149.99},
        {"min_quantity": 50, "price": 129.99}
      ],
      "group_prices": [
        {"customer_group_id": 1, "price": 179.99},
        {"customer_group_id": 2, "price": 159.99}
      ]
    },
    "attributes": [
      {"attribute_id": 1, "value": "Black", "auto_create_value": true},
      {"attribute_id": 3, "value": "Bluetooth 5.3", "auto_create_value": true},
      {"attribute_id": 7, "value": "40 hours", "auto_create_value": true}
    ],
    "categories": [5, 12, 18],
    "cross_sells": [45, 67],
    "up_sells": [89],
    "seo": {
      "slug": "premium-wireless-headphones-pro",
      "meta_title": "Premium Wireless Headphones | Best ANC Headphones 2024",
      "meta_description": "Shop premium wireless headphones with active noise cancellation. 40-hour battery, Bluetooth 5.3. Free shipping."
    }
  }'
```

#### 7.7 — Upsert Product by SKU

```bash
# Creates the product if SKU doesn't exist, updates if it does.
# Ideal for ERP/PIM synchronization.
curl -s -X PUT \
  'https://api.datahub.syncspider.com/api/v1/apps/product-hub/products/upsert/single' \
  -H 'Authorization: Bearer {token}' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "action": "createOrUpdate",
    "sku": "AUDIO-WH-PRO-001",
    "name": "Premium Wireless Headphones (Updated)",
    "status": "public",
    "prices": {
      "price": 209.99,
      "special_price": 179.99,
      "special_price_start_date": "2025-01-01",
      "special_price_end_date": "2025-03-31"
    },
    "stock": [
      {"warehouse_id": 1, "stock_quantity": 200}
    ]
  }'
```

#### 7.8 — Bulk Update Products

```bash
curl -s -X PUT \
  'https://api.datahub.syncspider.com/api/v1/apps/product-hub/products/bulk/update' \
  -H 'Authorization: Bearer {token}' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "products": [
      {"id": 101, "status": "private"},
      {"id": 102, "status": "private"},
      {"id": 103, "status": "public", "name": "Updated Product Name"}
    ]
  }'
```

#### 7.9 — Exclude Child Products / Show Only Parents

```bash
# Get only standalone and configurable parent products (no variations)
curl -s -X GET \
  'https://api.datahub.syncspider.com/api/v1/apps/product-hub/products?filter[exclude_child_products]=1&filter[product_type]=configurable&include=childProducts.childProduct.price,childProducts.childProduct.mainMedia,variationAttributes,price,mainMedia&page[size]=20' \
  -H 'Authorization: Bearer {token}' \
  -H 'Accept: application/json'
```

#### 7.10 — Products with Stock in Specific Warehouse

```bash
# Products with stock in warehouse 3, excluding out-of-stock
curl -s -X GET \
  'https://api.datahub.syncspider.com/api/v1/apps/product-hub/products?filter[stock.warehouse_id]=3&filter[without_stock]=1&include=stock,stock.warehouse,price,finalPrice,mainMedia&sort=-stock.stock_quantity&page[size]=30' \
  -H 'Authorization: Bearer {token}' \
  -H 'Accept: application/json'
```

---

## 8. SettingsHub

**Base URL:** `api/v1/apps/settings-hub/`

SettingsHub manages platform-wide configuration, translations, locales, currencies, countries, cache tracking, and search index management.

### Endpoints

#### Configuration

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/config` | List all configuration entries |
| POST | `/config` | Create a configuration entry |
| GET | `/config/{id}` | Get a specific configuration |
| PUT | `/config/{id}` | Update a configuration |
| DELETE | `/config/{id}` | Delete a configuration |

#### Translations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/translations` | List all translation entries |
| POST | `/translations` | Create a translation |
| GET | `/translations/{id}` | Get a specific translation |
| PUT | `/translations/{id}` | Update a translation |
| DELETE | `/translations/{id}` | Delete a translation |

#### Reference Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/locales` | List all available locales (en_US, de_DE, fr_FR, etc.) |
| GET | `/countries` | List all countries (name, iso2, iso3 codes) |
| GET | `/currencies` | List all currencies (cached from openexchangerates.org with fallback) |

#### Cache Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/cache` | List cache tracking entries |
| DELETE | `/clearAppCache/{installationKey}` | Clear application cache for a specific installation |

#### Index Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/index` | List all index tracking entries |
| PUT | `/index/{id}` | Update index configuration (e.g., manual vs on_save) |
| POST | `/index/queue` | Queue a reindex job |

### Filters

#### Config Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact config ID |
| `config_code` | text | Configuration key (e.g., `general.store_name`) |
| `value` | json | Configuration value (JSON match) |
| `installation_key` | json | Installation key filter |
| `display_schema` | json | FormGenerator display schema |

#### Translation Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact translation ID |
| `source` | text | Source/key string |
| `translations` | json | Translation JSON object |

#### Cache Tracking Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact cache entry ID |
| `installation_key` | text | Installation key |
| `application_name` | text | Application/hub name |
| `clear_required` | boolean | Whether cache clear is needed |

#### Index Tracking Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact index entry ID |
| `installation_key` | text | Installation key |
| `application_name` | text | Application/hub name |
| `type` | text | Index type |
| `model` | text | Model name |
| `reindex_required` | boolean | Whether reindex is needed |

### Includes

SettingsHub repositories do **not** expose any includes. All data is returned directly in the response without relation loading.

### Validation Rules

#### Config Store

| Field | Rules |
|-------|-------|
| `installation_key` | string · nullable |
| `config_code` | required · string |
| `value` | required (any JSON-compatible value) |

#### Translation Store

| Field | Rules |
|-------|-------|
| `source` | required · string |
| `translations` | required (object with locale keys) |

#### Index Update

| Field | Rules |
|-------|-------|
| `type` | required · in:manual,on_save |

#### Reindex Queue

| Field | Rules |
|-------|-------|
| `installation_key` | required |
| `model` | optional · in:stock,prices,attributes |

### Examples

#### 8.1 — List All Configuration

```bash
curl -s -X GET \
  'https://api.datahub.syncspider.com/api/v1/apps/settings-hub/config?filter[config_code]=general&page[size]=50' \
  -H 'Authorization: Bearer {token}' \
  -H 'Accept: application/json'
```

#### 8.2 — Get All Countries

```bash
curl -s -X GET \
  'https://api.datahub.syncspider.com/api/v1/apps/settings-hub/countries' \
  -H 'Authorization: Bearer {token}' \
  -H 'Accept: application/json'
```

Response includes name, iso2 (2-letter code), and iso3 (3-letter code) for every country.

#### 8.3 — Get All Currencies (Live Rates)

```bash
curl -s -X GET \
  'https://api.datahub.syncspider.com/api/v1/apps/settings-hub/currencies' \
  -H 'Authorization: Bearer {token}' \
  -H 'Accept: application/json'
```

Currencies are cached from openexchangerates.org. If the API is unavailable, a built-in fallback list is returned.

#### 8.4 — Trigger Reindex

```bash
curl -s -X POST \
  'https://api.datahub.syncspider.com/api/v1/apps/settings-hub/index/queue' \
  -H 'Authorization: Bearer {token}' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "installation_key": "my-store-key",
    "model": "prices"
  }'
```

---

## 9. TaxHub

**Base URL:** `api/v1/apps/tax-hub/`

TaxHub provides a flexible, rule-based tax calculation system with support for jurisdictions, VAT exemption, condition-based tax rules, and automatic tax rate imports for US, EU, and non-EU European countries.

### Endpoints

#### Settings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/settings/groups/list` | List all settings groups |
| GET | `/settings` | Get all tax settings |
| POST | `/settings` | Update tax settings (bulk) |
| POST | `/settings/reset` | Reset all settings to defaults |
| GET | `/settings/{group}` | Get settings for a specific group |
| POST | `/settings/{group}` | Update settings for a specific group |
| POST | `/settings/{group}/reset` | Reset a specific group to defaults |

#### Tax Classes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tax-classes` | List all tax classes |
| POST | `/tax-classes` | Create a tax class |
| GET | `/tax-classes/{id}` | Get tax class details |
| PUT | `/tax-classes/{id}` | Update a tax class |
| DELETE | `/tax-classes/{id}` | Delete a tax class |

#### Jurisdictions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/jurisdictions` | List all tax jurisdictions |
| POST | `/jurisdictions` | Create a jurisdiction |
| GET | `/jurisdictions/{id}` | Get jurisdiction details |
| PUT | `/jurisdictions/{id}` | Update a jurisdiction |
| DELETE | `/jurisdictions/{id}` | Delete a jurisdiction |

#### Tax Class Jurisdictions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tax-class-jurisdictions` | List all tax class ↔ jurisdiction mappings |
| POST | `/tax-class-jurisdictions` | Create a mapping with tax rate |
| GET | `/tax-class-jurisdictions/{id}` | Get mapping details |
| PUT | `/tax-class-jurisdictions/{id}` | Update a mapping |
| DELETE | `/tax-class-jurisdictions/{id}` | Delete a mapping |

#### Tax Rules

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tax-rules` | List all tax rules |
| POST | `/tax-rules` | Create a tax rule |
| GET | `/tax-rules/{id}` | Get tax rule details |
| PUT | `/tax-rules/{id}` | Update a tax rule |
| DELETE | `/tax-rules/{id}` | Delete a tax rule |
| GET | `/tax-rules/{id}/conditions` | List conditions for a tax rule |
| POST | `/tax-rules/{id}/conditions` | Add a condition to a tax rule |

#### Tax Rule Conditions

| Method | Endpoint | Description |
|--------|----------|-------------|
| PUT | `/tax-rule-conditions/{id}` | Update a rule condition |
| DELETE | `/tax-rule-conditions/{id}` | Delete a rule condition |

#### Tax Calculation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/calculate` | Calculate tax for line items |

#### Tax Rate Import

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/import/regions` | List available import regions |
| POST | `/import/{region}` | Import tax rates for a region (us, eu, non-eu-europe) |
| POST | `/import/refresh/all` | Refresh all imported tax rates |

### Filters

#### Tax Class Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact tax class ID |
| `name` | text | Tax class name |
| `description` | text | Tax class description |

#### Tax Rule Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact rule ID |
| `name` | text | Rule name |
| `status` | text | `active` or `inactive` |
| `priority` | number | Rule priority (lower = higher priority) |

#### Jurisdiction Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact jurisdiction ID |
| `name` | text | Jurisdiction name (e.g., "Germany", "California") |
| `code` | text | Jurisdiction code (e.g., "DE", "US-CA") |

#### Tax Class Jurisdiction Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact mapping ID |
| `tax_class_id` | number | Tax class ID |
| `jurisdiction_id` | number | Jurisdiction ID |
| `tax_rate` | number | Tax rate percentage |

#### Tax Rule Condition Filters

| Filter Key | Type | Description |
|------------|------|-------------|
| `id` | number | Exact condition ID |
| `tax_rule_id` | number | Parent rule ID |
| `condition_type` | text | Condition type |

### Includes

#### Tax Class Includes

| Include | Description |
|---------|-------------|
| `translation` | Tax class translations |

#### Tax Rule Includes

| Include | Description |
|---------|-------------|
| `conditions` | All conditions attached to this rule |
| `taxClassJurisdiction` | The tax class ↔ jurisdiction mapping this rule applies |
| `translation` | Tax rule translations |

#### Jurisdiction Includes

| Include | Description |
|---------|-------------|
| `translation` | Jurisdiction translations |

#### Tax Class Jurisdiction Includes

| Include | Description |
|---------|-------------|
| `translation` | Mapping translations |
| `taxClass` | The tax class |
| `jurisdiction` | The jurisdiction |

#### Tax Rule Condition Includes

| Include | Description |
|---------|-------------|
| `taxRule` | Parent tax rule |
| `translation` | Condition translations |

### Validation Rules

#### Create Tax Rule

| Field | Rules |
|-------|-------|
| `name` | required · string |
| `description` | nullable · string |
| `priority` | required · integer · min:0 |
| `status` | required · in:active,inactive |
| `match_type` | required · in:all,any (how to combine conditions) |
| `tax_class_jurisdiction_id` | required · integer (which tax rate to apply) |

#### Add Condition to Rule

| Field | Rules |
|-------|-------|
| `condition_type` | required · in:customer_email,email_domain,country,region,customer_group,vat_number |
| `operator` | required · in:equals,contains,starts_with,ends_with,in,not_in,is_empty,is_not_empty |
| `value` | nullable · string (the value to match against) |

### Tax Calculation

#### POST `/calculate`

The tax calculation engine evaluates rules and jurisdictions to determine the correct tax for each line item.

**Request Body:**

```json
{
  "line_items": [
    {
      "subtotal": 100.00,
      "tax_class_id": 1,
      "product_id": 5
    },
    {
      "subtotal": 49.99,
      "tax_class_id": 2,
      "product_id": 12
    }
  ],
  "customer": {
    "email": "customer@example.com",
    "country": "DE",
    "region": "Bavaria",
    "customer_group": "retail",
    "vat_number": "DE123456789"
  }
}
```

**Tax Calculation Fallback Chain:**

The engine resolves tax rates using this priority order:

```
1. Matched tax rule (conditions match customer data)
       ↓ (no match)
2. Tax class + jurisdiction (direct mapping)
       ↓ (no mapping)
3. Country-level tax rate
       ↓ (no country rate)
4. GLOBAL jurisdiction rate
       ↓ (no global rate)
5. Config default tax rate
```

**Country Resolution Chain:**

When determining the customer's country:

```
1. Billing address country
       ↓ (not available)
2. Shipping address country
       ↓ (not available)
3. Default country from SettingsHub config
```

### Settings Groups

#### `general` — General Tax Settings

| Setting | Type | Description |
|---------|------|-------------|
| `enable_tax_rules` | boolean | Enable/disable rule-based tax calculation |
| `default_tax_class_id` | number | Default tax class for products without one |
| `default_jurisdiction_id` | number | Default jurisdiction |
| `default_country_tax` | number | Fallback tax rate by country |
| `log_tax_calculations` | boolean | Enable calculation logging for debugging |

#### `calculation` — Calculation Settings

| Setting | Type | Description |
|---------|------|-------------|
| `tax_calculation_method` | string | Calculation method (per item, per row, total) |
| `tax_rounding_mode` | string | Rounding mode (round, ceil, floor) |
| `prices_include_tax` | boolean | Whether catalog prices are tax-inclusive |

#### `product_pricing` — Product Pricing Display

| Setting | Type | Description |
|---------|------|-------------|
| `price_entry_mode` | string | How prices are entered (excl_tax, incl_tax) |
| `display_prices_with_tax` | boolean | Display prices with tax in storefront |
| `final_price_includes_tax` | boolean | Whether final computed price includes tax |

#### `vat` — VAT Settings

| Setting | Type | Description |
|---------|------|-------------|
| `enable_vat_exemption` | boolean | Enable VAT exemption for B2B customers with valid VAT numbers |

#### `import` — Tax Rate Import Settings

| Setting | Type | Description |
|---------|------|-------------|
| `auto_refresh_enabled` | boolean | Automatically refresh imported tax rates |
| `taxrate_io_api_key` | string | API key for taxrate.io service |
| `last_refresh_at` | datetime | Last successful refresh timestamp |

**Available Import Regions:** `us`, `eu`, `non-eu-europe`

### Examples

#### 9.1 — List Tax Rules with Conditions

```bash
curl -s -X GET \
  'https://api.datahub.syncspider.com/api/v1/apps/tax-hub/tax-rules?include=conditions,taxClassJurisdiction,taxClassJurisdiction.taxClass,taxClassJurisdiction.jurisdiction&filter[status]=active&sort=priority' \
  -H 'Authorization: Bearer {token}' \
  -H 'Accept: application/json'
```

#### 9.2 — Create Tax Rule with Condition

```bash
# Step 1: Create the rule
curl -s -X POST \
  'https://api.datahub.syncspider.com/api/v1/apps/tax-hub/tax-rules' \
  -H 'Authorization: Bearer {token}' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "name": "EU B2B VAT Exemption",
    "description": "Zero-rate VAT for B2B customers with valid EU VAT numbers",
    "priority": 10,
    "status": "active",
    "match_type": "all",
    "tax_class_jurisdiction_id": 5
  }'

# Step 2: Add conditions to the rule (assuming rule ID 7 was returned)
curl -s -X POST \
  'https://api.datahub.syncspider.com/api/v1/apps/tax-hub/tax-rules/7/conditions' \
  -H 'Authorization: Bearer {token}' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "condition_type": "vat_number",
    "operator": "is_not_empty",
    "value": null
  }'

curl -s -X POST \
  'https://api.datahub.syncspider.com/api/v1/apps/tax-hub/tax-rules/7/conditions' \
  -H 'Authorization: Bearer {token}' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "condition_type": "country",
    "operator": "in",
    "value": "DE,FR,NL,BE,AT,IT,ES,PT,IE,FI,SE,DK,PL,CZ,SK,HU,RO,BG,HR,SI,EE,LV,LT,LU,MT,CY,GR"
  }'
```

#### 9.3 — Calculate Tax for B2C Customer

```bash
curl -s -X POST \
  'https://api.datahub.syncspider.com/api/v1/apps/tax-hub/calculate' \
  -H 'Authorization: Bearer {token}' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "line_items": [
      {"subtotal": 199.99, "tax_class_id": 1, "product_id": 105},
      {"subtotal": 14.50, "tax_class_id": 1, "product_id": 210},
      {"subtotal": 9.99, "tax_class_id": 3, "product_id": 301}
    ],
    "customer": {
      "email": "hans.mueller@gmail.com",
      "country": "DE",
      "region": "Bavaria",
      "customer_group": "retail"
    }
  }'
```

#### 9.4 — Calculate Tax for B2B Customer (with VAT Number)

```bash
curl -s -X POST \
  'https://api.datahub.syncspider.com/api/v1/apps/tax-hub/calculate' \
  -H 'Authorization: Bearer {token}' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "line_items": [
      {"subtotal": 5000.00, "tax_class_id": 1, "product_id": 500},
      {"subtotal": 1200.00, "tax_class_id": 2, "product_id": 601}
    ],
    "customer": {
      "email": "procurement@acme-gmbh.de",
      "country": "DE",
      "region": "Hessen",
      "customer_group": "wholesale",
      "vat_number": "DE123456789"
    }
  }'
```

If the "EU B2B VAT Exemption" rule from example 9.2 is active, this will match and apply the zero-rate tax class jurisdiction.

#### 9.5 — Import EU Tax Rates

```bash
curl -s -X POST \
  'https://api.datahub.syncspider.com/api/v1/apps/tax-hub/import/eu' \
  -H 'Authorization: Bearer {token}' \
  -H 'Accept: application/json'
```

This imports standard VAT rates for all EU member states. Also available: `POST /import/us` (US state sales tax) and `POST /import/non-eu-europe` (Switzerland, Norway, UK, etc.).

#### 9.6 — Filter Tax Class Jurisdictions

```bash
curl -s -X GET \
  'https://api.datahub.syncspider.com/api/v1/apps/tax-hub/tax-class-jurisdictions?filter[tax_class_id]=1&include=taxClass,jurisdiction&sort=tax_rate&page[size]=50' \
  -H 'Authorization: Bearer {token}' \
  -H 'Accept: application/json'
```

---

## Quick Reference — All Hubs (Part 2)

| Hub | Base URL | Key Entities | Filters | Includes |
|-----|----------|-------------|---------|----------|
| **OrderHub** | `order-hub/` | Orders, Carts, Line Items, Checkout, Quotes, Billing/Shipping Methods | 10+ per entity | Deep: customer, products, addresses, attributes |
| **ProductHub** ⭐ | `product-hub/` | Products, Categories, Stock, Prices, Media, Vendors, Translations | **26 product filters**, 7+ per sub-entity | **42+ includes** with deep nesting |
| **SettingsHub** | `settings-hub/` | Config, Translations, Locales, Countries, Currencies, Cache, Index | 4-5 per entity | None |
| **TaxHub** | `tax-hub/` | Tax Classes, Rules, Conditions, Jurisdictions, Calculation, Import | 3-5 per entity | conditions, taxClass, jurisdiction |

---

*Generated for DataHub Platform. See Part 1 for hubs 1–5 (AttributesHub, CustomerHub, LicenseHub, NotificationHub, MediaHub).*
