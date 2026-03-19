# Build DataHub API Filter Query

Help build a correct filter query for the DataHub API.

## Instructions

The user describes what data they want to filter. You should:

1. **Identify the hub and resource** they're filtering
2. **Read the relevant hub docs** to find available filter fields
3. **Read `core-concepts/filtering.mdx`** for filter syntax reference
4. **Build the correct filter query** using the MongoDB-compatible JSON syntax:
   - Standard filters: `?filter[field]=[{"condition":"operator","value":"value"}]`
   - Callback filters: `?filter[search]=term`
   - Relation filters: `?filter[company.name]=[...]`
   - Attribute filters: `?filter[attribute]=[{"attribute_id":1,...}]`
5. **Provide the complete curl command** with proper URL encoding
6. **Suggest relevant includes** that would complement the filter
7. **Add sorting** if appropriate

Common pitfalls to warn about:
- Filter values must be JSON-encoded arrays (except callback filters)
- `IN` is preferred over chaining `OR` conditions
- Use `anchor_category_id` instead of `categories.category_id` for category trees
- Use `exclude_child_products=1` to hide variations in listings

## User Input

$ARGUMENTS
