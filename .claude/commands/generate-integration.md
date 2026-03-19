# Generate DataHub API Integration

Generate integration code for the B2Bware DataHub API based on user requirements.

## Instructions

The user wants to generate integration code for the DataHub API. Ask them (or use the provided info) to determine:

1. **Which hub(s)** to integrate with (ProductHub, OrderHub, CustomerHub, etc.)
2. **Which language/framework** (Node.js/TypeScript, Python, PHP/Laravel, etc.)
3. **What operations** (list, create, update, upsert, bulk, checkout, etc.)

Then generate clean, production-ready code that:

- Uses environment variables for `DATAHUB_DOMAIN` and `DATAHUB_TOKEN`
- Sets all required headers: `Authorization: Bearer {token}`, `Accept: application/json`, `Content-Type: application/json`
- Handles pagination (iterate `current_page` to `last_page`)
- Handles errors properly (check HTTP status, parse validation errors from 422)
- Uses appropriate includes and filters
- Uses upsert endpoints for sync workflows where applicable
- Follows the coding conventions from CLAUDE.md

Read the relevant hub documentation file (e.g., `hubs/product-hub.mdx`) for the specific endpoints, filters, includes, and validation rules needed.

## User Input

$ARGUMENTS
