# Generate ERP Sync Integration

Generate code for syncing data between an ERP system and DataHub.

## Instructions

The user wants to sync data between an external system (ERP, PIM, etc.) and DataHub. Generate a complete sync solution that:

1. **Uses upsert endpoints** for idempotent operations:
   - Products: `PUT /product-hub/products/upsert/single` with `action: "createOrUpdate"` and SKU as key
   - Stock: `POST /product-hub/stock/upsert/bulk`
   - Prices: `POST /product-hub/prices/upsert/bulk`
   - Translations: `PUT /product-hub/translations/upsert/bulk`

2. **Handles the sync flow**:
   - Fetch data from source system
   - Transform to DataHub format (validate against rules in hub docs)
   - Upsert in correct order: Products first, then stock/prices/attributes
   - Handle errors per-item (bulk endpoints return per-item errors)
   - Log results

3. **Best practices**:
   - Batch requests (max ~1000 items per bulk call)
   - Use exponential backoff for 5xx errors
   - Never retry 4xx without fixing the request
   - Store external IDs via `external_id` field on orders
   - Use `filter[sku]` to look up existing products

4. **Read relevant docs**:
   - `hubs/product-hub.mdx` for product validation rules
   - `advanced/bulk-operations.mdx` for bulk operation patterns
   - `hubs/order-hub.mdx` if syncing orders

## User Input

$ARGUMENTS
