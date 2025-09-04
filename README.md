# eShop

eShop is a mini E-commerce app that can be embedded or integrated into other platforms, enabling them to sell products or services online with minimal setup. The app will be **self-contained**, providing product management, shopping cart, checkout, and payment features **out of the box**.

### Requirement
This project is expected to be:
- **Modular**: can be installed as a standalone API or embedded into an existing application
- **Customizable**: host platforms can configure it to match their need.
- **API-driven**: the backend exposes a clear API that can be used by any frontend.
- **Secure**: Handles transactions, payments, and customer data safely

## Core Features
1. Product Management:
   - [x] Host can add, edit, delete products
   - [x] Product categories and tags
   - [x] Product images and description
   - [x] Stock quantity management
   - [x] Set low stock reminder
   - [x] Pricing
   - [x] Digital and physical product support
   - [ ] Enable sub-category
   - [ ] Enable product variant
   - [x] Allow backorder on empty stock

2. Shopping cart:
   - [x] Add/remove products to cart
   - [x] Update cart quantities
   - [ ] Discount and Coupon codes
   - [x] Support delivery
   - [ ] Shipping and delivery options (e.g. Pick up)

3. Payments
   - [x] Payment gateway integrations (Stripe, PayPal, Flutterwave, Paystack)
   - [ ] Cash-on-delivery option

4. Order Management
   - [x] Order creation & status tracking
   - [x] Order status updates (pending, shipped, delivered, cancelled)
   - [ ] Invoice generation
   - [ ] Email/SMS notifications

5. User Accounts
   - [x] Customer registration & login (email or social login)
   - [ ] View past orders
   - [ ] Manage shipping addresses

6. Product Review
   - [x] Customer review on product

7. Admin API
   - [ ] Admin API to manage store and products


### Other features include:
- [x] Setting up proper and robost logging across all app.
- [ ] Background job processing to speadup app performance when faced with time consuming task
- [ ] Caching
- [ ] Pagination
- [ ] Throttling
