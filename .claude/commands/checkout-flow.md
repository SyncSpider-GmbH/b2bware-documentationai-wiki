# Implement Checkout Flow

Generate a complete cart-to-order checkout implementation.

## Instructions

The user wants to implement the DataHub checkout flow. Read `advanced/checkout-flow.mdx` and `hubs/order-hub.mdx`, then generate code that implements:

### Flow Steps

1. **Create/Upsert Cart**
   - `POST /order-hub/carts` (customer cart with customer_id)
   - `PATCH /order-hub/carts` (guest cart, upsert by session_uuid)
   - Include cart_items with product_id and quantity

2. **Load Cart with Product Data**
   - `GET /order-hub/carts/{id}?include=cartItems.product.price,cartItems.product.finalPrice,cartItems.product.mainMedia,cartItems.product.crossSells,customer`

3. **Manage Cart Items**
   - Add: `POST /order-hub/cart-items`
   - Update quantity: `PUT /order-hub/cart-items/{id}`
   - Remove: `DELETE /order-hub/cart-items/{id}`

4. **Preview Checkout**
   - `GET /order-hub/carts/{id}/checkout`
   - Shows calculated totals, shipping costs, tax

5. **Complete Checkout**
   - `POST /order-hub/carts/{id}/checkout`
   - Required: shipping_method_id, billing_method_id, shipping_address_id, billing_address_id
   - Optional: comment

6. **Handle the Created Order**
   - Load order with includes: `customer,orderLineItems,shippingMethod,billingMethod`
   - Order statuses: draft, pending, invoiced, shipped, completed, pending_payment, paid, refunded, partially_refunded, canceled, processing

Also reference `advanced/tax-calculation.mdx` for tax handling during checkout.

## User Input

$ARGUMENTS
