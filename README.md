# ShopAPI

Production-ready e-commerce REST API built with Django, Django REST Framework, PostgreSQL, Redis, Celery, JWT authentication, and OpenAPI documentation.

ShopAPI provides the core backend flows for an online store: account registration and login, product catalog management, cart operations, checkout, order tracking, and simulated payments.

## Features

- Custom email-based user model
- JWT authentication with access and refresh tokens
- Product and category CRUD
- Public read access for catalog data
- Staff-only catalog writes
- User cart with add, update, remove, and clear actions
- Checkout flow that creates orders, order items, reduces stock, and clears the cart
- Simulated payment endpoint that marks orders as paid or failed
- Celery tasks for order confirmation email and invoice generation
- Redis-backed caching and Celery broker/result backend
- PostgreSQL database
- Swagger UI and OpenAPI schema via drf-spectacular
- Docker and Docker Compose support

## Tech Stack

- Python 3.13
- Django 5.2+
- Django REST Framework
- Simple JWT
- django-filter
- drf-spectacular
- PostgreSQL
- Redis
- Celery
- Gunicorn
- Docker

## Project Structure

```text
ShopAPI/
|-- accounts/      # Custom user model, registration, login, profile APIs
|-- products/      # Categories, products, catalog permissions, caching
|-- cart/          # User cart and cart item operations
|-- orders/        # Checkout, orders, order items, Celery tasks
|-- payments/      # Payment records and simulated payment flow
|-- common/        # Shared pagination, cache helpers, exceptions
|-- ShopAPI/       # Django settings, urls, ASGI/WSGI, Celery app
|-- Dockerfile
|-- docker-compose.yml
|-- manage.py
`-- requirements.txt
```

## Requirements

For Docker setup:

- Docker
- Docker Compose

For local setup:

- Python 3.13+
- PostgreSQL
- Redis

## Environment Variables

Create a `.env` file in the project root. You can start from `.env.example`.

```env
SECRET_KEY=change-me-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
TIME_ZONE=UTC

POSTGRES_DB=shopapi
POSTGRES_USER=shopapi
POSTGRES_PASSWORD=shopapi
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CELERY_TASK_ALWAYS_EAGER=False

JWT_ACCESS_MINUTES=30
JWT_REFRESH_DAYS=7
PAGE_SIZE=20
LOG_LEVEL=INFO
DEFAULT_FROM_EMAIL=noreply@shopapi.local
```

For local development outside Docker, set:

```env
POSTGRES_HOST=localhost
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Run With Docker

Build and start all services:

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

Run migrations manually if needed:

```bash
docker compose exec web python manage.py migrate
```

Create an admin user:

```bash
docker compose exec web python manage.py createsuperuser
```

Stop services:

```bash
docker compose down
```

Stop services and remove database volume:

```bash
docker compose down -v
```

## Run Locally

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Apply migrations:

```bash
python manage.py migrate
```

Create an admin user:

```bash
python manage.py createsuperuser
```

Run the API server:

```bash
python manage.py runserver
```

Run the Celery worker in another terminal:

```bash
celery -A ShopAPI worker -l info
```

## API Documentation

Swagger UI:

```text
GET /api/docs/
```

OpenAPI schema:

```text
GET /api/schema/
```

DRF API root:

```text
GET /api/
```

## Authentication

The API uses JWT bearer authentication.

Register:

```http
POST /api/auth/
Content-Type: application/json

{
  "email": "customer@example.com",
  "password": "strong-password",
  "first_name": "Customer",
  "last_name": "One"
}
```

Login:

```http
POST /api/auth/login/
Content-Type: application/json

{
  "email": "customer@example.com",
  "password": "strong-password"
}
```

Use the returned access token:

```http
Authorization: Bearer <access_token>
```

## API Routes

All application routes are mounted under `/api/`.

### Auth

| Method | Route | Description | Auth |
| --- | --- | --- | --- |
| POST | `/api/auth/` | Register a new user | Public |
| POST | `/api/auth/login/` | Login and receive JWT tokens | Public |
| GET | `/api/auth/profile/` | Get current user profile | User |
| PATCH | `/api/auth/profile/` | Update current user profile | User |

### Categories

Category detail routes use `slug` as the lookup field.

| Method | Route | Description | Auth |
| --- | --- | --- | --- |
| GET | `/api/categories/` | List categories | Public |
| POST | `/api/categories/` | Create category | Staff |
| GET | `/api/categories/{slug}/` | Get category | Public |
| PUT | `/api/categories/{slug}/` | Replace category | Staff |
| PATCH | `/api/categories/{slug}/` | Update category | Staff |
| DELETE | `/api/categories/{slug}/` | Delete category | Staff |

### Products

| Method | Route | Description | Auth |
| --- | --- | --- | --- |
| GET | `/api/products/` | List active products | Public |
| POST | `/api/products/` | Create product | Staff |
| GET | `/api/products/{id}/` | Get product | Public |
| PUT | `/api/products/{id}/` | Replace product | Staff |
| PATCH | `/api/products/{id}/` | Update product | Staff |
| DELETE | `/api/products/{id}/` | Delete product | Staff |

Supported product filters and query helpers:

```text
?category=<category_id>
?category__slug=<slug>
?is_active=true
?search=<term>
?ordering=price
?ordering=-created_at
```

### Cart

| Method | Route | Description | Auth |
| --- | --- | --- | --- |
| GET | `/api/cart/` | Get current user's cart | User |
| POST | `/api/cart/add_item/` | Add product to cart | User |
| PATCH | `/api/cart/items/{item_id}/` | Update cart item | User |
| DELETE | `/api/cart/items/{item_id}/` | Remove cart item | User |
| DELETE | `/api/cart/clear/` | Clear cart | User |

Add item payload:

```json
{
  "product_id": 1,
  "quantity": 2
}
```

Update item payload:

```json
{
  "quantity": 3
}
```

Note: the current cart view defines separate `PATCH` and `DELETE` actions with the same `items/{item_id}` URL path. If `DELETE /api/cart/items/{item_id}/` returns `405 Method Not Allowed`, combine those methods into one DRF action.

### Orders

| Method | Route | Description | Auth |
| --- | --- | --- | --- |
| GET | `/api/orders/` | List current user's orders | User |
| GET | `/api/orders/{id}/` | Get order detail | User |
| POST | `/api/orders/checkout/` | Checkout current cart | User |

Checkout creates an order from the authenticated user's cart, copies cart items into order items, reduces product stock, clears the cart, and queues an order confirmation email.

### Payments

| Method | Route | Description | Auth |
| --- | --- | --- | --- |
| GET | `/api/payments/` | List current user's payments | User |
| GET | `/api/payments/{id}/` | Get payment detail | User |
| POST | `/api/payments/simulate/` | Simulate payment result | User |

Simulate payment payload:

```json
{
  "order_id": 1,
  "success": true
}
```

When `success` is `true`, the payment is marked as successful, the order is marked as paid, and invoice generation is queued.

## Example Flow

1. Register a user with `POST /api/auth/`.
2. Login with `POST /api/auth/login/`.
3. Use the access token in the `Authorization` header.
4. As staff, create categories and products.
5. As a user, browse products with `GET /api/products/`.
6. Add products to cart with `POST /api/cart/add_item/`.
7. Checkout with `POST /api/orders/checkout/`.
8. Simulate payment with `POST /api/payments/simulate/`.

## Pagination

List endpoints use the default page size from `PAGE_SIZE`, which defaults to `20`.

Example:

```text
GET /api/products/?page=2
```

## Background Jobs

Celery is configured through `ShopAPI/celery.py` and uses Redis by default.

Current tasks:

- `send_order_confirmation_email(order_id)`
- `generate_invoice_pdf(order_id)`

For development without a worker, you can set:

```env
CELERY_TASK_ALWAYS_EAGER=True
```

## Admin

Django admin is available at:

```text
/admin/
```

Create a superuser before logging in:

```bash
python manage.py createsuperuser
```

With Docker:

```bash
docker compose exec web python manage.py createsuperuser
```

## Development Notes

- Public users only see active products.
- Staff users can see and manage inactive products.
- Category detail uses `slug`, not numeric `id`.
- Product writes require a staff user.
- Cart and order data is scoped to the authenticated user.
- Payment simulation only accepts pending orders for the authenticated user.
- Product stock is reduced during checkout, not during cart add.
- Payments are one-to-one with orders.

## License

No license file is currently included. Add a license before distributing this project publicly.
