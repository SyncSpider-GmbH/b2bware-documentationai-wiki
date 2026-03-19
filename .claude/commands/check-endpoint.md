# Validate DataHub API Endpoint Usage

Validate an API call against the DataHub documentation to check for errors.

## Instructions

The user will provide an API call (curl command, code snippet, or endpoint description). You should:

1. **Identify the hub and endpoint** from the URL pattern
2. **Read the relevant hub documentation** file (e.g., `hubs/product-hub.mdx`)
3. **Validate**:
   - Is the endpoint URL correct? (correct hub slug, resource path, HTTP method)
   - Are the required headers present? (Authorization, Accept, Content-Type)
   - Are the filter parameters using correct JSON syntax and valid operators?
   - Are the include names valid for this resource?
   - Does the request body match the validation rules?
   - Are required fields present?
   - Are enum values correct? (status, product_type, etc.)
4. **Report**:
   - Any errors or issues found
   - Suggestions for improvement (better includes, missing filters, etc.)
   - Working corrected version if there were errors

## User Input

$ARGUMENTS
