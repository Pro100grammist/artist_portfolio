# Artist Portfolio - Django Web Application

## Project description

**Artist Portfolio** is a web application for an artist's online portfolio with the ability to showcase and sell works. The project is based on **Django 5.1**, **REST API** for interaction between backend and frontend. In addition to the main web interface (HTML, CSS, JavaScript), a separate application on **Vue.js** is responsible for rendering a 3D gallery of paintings.

### Main functions:
- Manage artist's works through the admin panel.
- Viewing paintings in 3D format (Vue.js + Three.js).
- REST API for working with the frontend.
- Online store with support for filters, sorting, and searching for paintings.
- An alternative option for authorization via Google and Facebook.
- Account protection via 2FA (OTP).
- Integration with payment systems.

---

## Technology

### **Backend (Django)**
- Django 5.1 - the main framework
- Django REST Framework ** - building an API
- **Celery + Redis** - asynchronous task processing
- Django Channels - WebSocket connection
- **SQLite (optional PostgreSQL)** - database
- **Gunicorn + Whitenoise** - deployment and processing of static

### **Frontend**
- **HTML + CSS + JavaScript** – UI
- **Vue.js + Three.js** – 3D rendering for 2D paintings from the gallery

---

## Installation and startup

### **1. Cloning the repository** **2.
```bash
git clone https://github.com/your_username/artist_portfolio.git
cd artist_portfolio
```

### **2. Setting up the environment****.
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

Create an `.env' file in artist_portfolio dir with variables:
```
DJANGO_ENV=development
SECRET_KEY=your_secret_key
STRIPE_SECRET_KEY=sk_test_your_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
PAYMENT_DEFAULT_CURRENCY=usd
STRIPE_WEBHOOK_TOLERANCE=300

#optional
EMAIL_HOST_PASSWORD=your_email_host_password
CLIENT_ID=Google Client ID 
CLIENT_SECRET=Google Client
API_KEY
PHONE_NUMBER
DATABASE_URL=sqlite:///db.sqlite3  # or PostgreSQL
REDIS_URL=redis://localhost:6379/0

# optional emergency toggles
ENABLE_PRODUCTION_SECURITY=true
ENABLE_CSP=true
ENABLE_RATE_LIMITING=true
```

### **3. Database migrations**
```bash
python manage.py migrate
python manage.py createsuperuser
```

### **4. Launching servers**
```bash
python manage.py runserver  # Django API
celery -A artist_portfolio worker --loglevel=info  # Celery
redis-server  # Redis
```

### **5. Зlaunching a 3D gallery (Vue.js)**
```bash
cd frontend/3d-gallery
npm install
npm run serve
```

---

## API documentation
The project uses **drf-spectacular** to automatically generate API documentation.

- OpenAPI scheme: [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)
- Swagger UI: [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)
- ReDoc: [http://localhost:8000/api/schema/redoc/](http://localhost:8000/api/schema/redoc/)

---

## Stripe checkout and webhook lifecycle

- Checkout now creates a Stripe Checkout Session on the backend and redirects the customer to Stripe.
- Orders remain in `AwaitingPayment` until a verified Stripe webhook confirms success.
- The authoritative webhook endpoint is `/order/stripe/webhook/`.
- `OrderPayment` stores the active provider payment attempt and `PaymentEvent` stores webhook processing state for idempotency and replay safety.

### Local webhook testing

1. Start Django locally:
```bash
cd artist_portfolio
python manage.py runserver
```

2. Start Stripe CLI forwarding:
```bash
stripe login
stripe listen --forward-to http://127.0.0.1:8000/order/stripe/webhook/
```

3. Copy the signing secret printed by Stripe CLI into `.env`:
```bash
STRIPE_WEBHOOK_SECRET=whsec_...
```

4. Create a checkout session through the site, or trigger a webhook event manually:
```bash
stripe trigger checkout.session.completed
stripe trigger payment_intent.payment_failed
```

### Operational notes

- Monitor `OrderPayment` and `PaymentEvent` in Django admin for stuck `pending` payments, unprocessed webhook events, and repeated provider retries.
- The webhook handler returns `400` for bad signatures or malformed payloads, `200` for already-processed replays, and `500` when a verified event cannot be processed safely and should be retried.
- Amount and currency are validated against the saved order/payment before an order can move to `Paid`.
- If a verified webhook fails with `500`, fix the underlying issue first and then replay the same Stripe event from the Stripe Dashboard or Stripe CLI. The event log makes the replay idempotent.

---

## Deployment

For production deployments, we recommend using:
- **Gunicorn** for the backend
- **NGINX** for request processing
- **Docker + Docker Compose** (optional)

## Security hardening

Production security hardening is enabled when `DJANGO_ENV=production`.

- Django now enforces HTTPS redirects, secure session and CSRF cookies, HSTS, and `SECURE_PROXY_SSL_HEADER`.
- Rate limiting protects the login page (`5/m`), the contact form (`10/m`), and cart mutations (`10/m`).
- CSP is enabled in production with an allowlist for the current CDNs, Google Fonts, Google Maps, and the Backblaze media host. Admin, Jet, and schema docs are excluded because those vendor UIs rely on inline assets outside this task's scope.

### Reverse proxy requirement

Your reverse proxy must forward `X-Forwarded-Proto: https` for HTTPS requests. Example NGINX snippet:

```nginx
proxy_set_header X-Forwarded-Proto $scheme;
```

If this header is missing in production, `SECURE_SSL_REDIRECT=True` can cause redirect loops.

### Emergency rollback

If you need a temporary rollback without changing code:

- Set `ENABLE_CSP=false` to disable CSP headers.
- Set `ENABLE_RATE_LIMITING=false` to disable `429` throttling.
- Set `ENABLE_PRODUCTION_SECURITY=false` to disable the production-only SSL/HSTS/secure-cookie bundle.

These flags should only be used as short-lived incident mitigations and then reverted.

---

## Contribution to the project
The project is open for contributions! To do this:
1. Create a repository.
2. Make changes in your branch.
3. Submit a pull request.

### Author: Pro100grammer

### License.
This project is distributed under the MIT license.
