# Explain a DataHub Hub

Provide a comprehensive explanation of a specific DataHub hub.

## Instructions

The user wants to understand a specific hub. Read the relevant hub documentation file and provide:

1. **Overview**: What the hub does and its base URL
2. **All endpoints**: Grouped by resource type with HTTP methods
3. **Available filters**: All filterable fields with types
4. **Available includes**: All include options with descriptions
5. **Validation rules**: Required and optional fields for create/update
6. **Code examples**: Practical curl examples for common operations
7. **Related hubs**: How this hub connects to other hubs

Read the hub documentation from: `hubs/{hub-name}.mdx`

Also reference:
- `core-concepts/filtering.mdx` for filter syntax
- `core-concepts/includes.mdx` for include patterns
- Any relevant `advanced/` guides

## User Input

$ARGUMENTS
