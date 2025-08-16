# eShop

eShop is a mini E-commerce app that can be embedded or integrated into other platforms, enabling them to sell products or services online with minimal setup. The app will be **self-contained**, providing product management, shopping cart, checkout, and payment featues **out of the box**.

### Requirement
This project is expected to be:
- **Modular**: can be installed as a standalone API or embedded into an existing application
- **Customizable**: host platforms can configure it to match their need.
- **API-driven**: the backend exposes a clear API that can be used by any frontend.
- **Secure**: Handles transactions, payments, and customer data safely

## Core Features
1. Product Management:
   - [ ] Host can add, edit, delete products
   - [ ] Product categories and tags
   - [ ] Product images and description
   - [ ] Stock quantity management
   - [ ] Set low stock reminder
   - [ ] Pricing
   - [ ] Digital and physical product support
   - [ ] Enable sub-category
   - [ ] Enable product variant
   - [ ] Allow backorder on empty stock

2. Shopping cart:
   - [ ] Add/remove products to cart
   - [ ] Update cart quantities
   - [ ] Discount and Coupon codes
   - [ ] Shipping and delivery options

3. Payments
   - [ ] Payment gateway integrations (Stripe, PayPal, Flutterwave, Paystack)
   - [ ] Cash-on-delivery option

4. Order Management
   - [ ] Order creation & tracking
   - [ ] Order status updates (pending, shipped, delivered, cancelled)
   - [ ] Invoice generation
   - [ ] Email/SMS notifications

5. User Accounts
   - [ ] Customer registration & login (email or social login)
   - [ ] View past orders
   - [ ] Manage shipping addresses

6. Product Review
   - [ ] Customer review on product


### Other features include:
- [ ] Setting up proper and robost logging across all app.
- [ ] Background job processing to speadup app performance when faced with time consuming task
- [ ] Caching
- [ ] Pagination
- [ ] Throttling
