""" for later"""
# Add __repr__ methods to models to ease debugging.

# Consider adding a created_at timestamp column for restaurants and menu items.

# You might want to create async CRUD helper functions for reuse as your project grows.


# Authentication (login, roles)

# Pagination & filtering

# Async DB operations

# Background jobs (sending emails, cleaning up records)

# Deployment to cloud (Docker, Kubernetes)


"""for search endpoint"""
# Use pagination (limit, offset),

# Or support sorting (order_by=release_year).


🔹 Step 1: Requirements from your boss

Customers should be able to:

Browse restaurants & menus

Place orders

Track delivery status

Restaurants should be able to:

Receive orders

Update order status (accepted, being prepared, ready)

Couriers should be able to:

See available deliveries

Update delivery progress (picked up, delivered)

🔹 Step 2: Tasks you’ll be asked to do

Design the database

Tables: users, restaurants, menus, orders, order_items, deliveries.

Write API endpoints

For each feature above, create endpoints.

Add authentication (customers, couriers, restaurants log in separately).

Make sure API returns JSON responses (so frontend can easily consume them).

🔹 Step 3: Example API endpoints you’d create

For customers:

GET /restaurants → list all restaurants

GET /restaurants/{id}/menu → get menu for a restaurant

POST /orders → place a new order

GET /orders/{id} → check order status

For restaurants:

GET /orders/new → list incoming orders

PUT /orders/{id}/status → update status (accepted, ready, etc.)

For couriers:

GET /deliveries/available → see available deliveries

PUT /deliveries/{id}/status → update delivery progress (picked up, delivered)

🔹 Step 4: Real life challenge you’d face

Authentication → You’d implement login with JWT tokens.

Security → Customers shouldn’t be able to mark orders as “delivered,” only couriers can.

Scalability → What if 10,000 people order at the same time? You’d think about caching & queues.

Integrations → You might need to connect with a payment API (Stripe, PayPal) for checkout.

🔹 Step 5: The daily workflow

Morning standup: your PM says “Today we need the order tracking API so the app can show delivery status in real-time.”

You open your code editor, write something like: