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

SECRET_KEY=your_secret_key

#optional
EMAIL_HOST_PASSWORD=your_email_host_password
CLIENT_ID=Google Client ID 
CLIENT_SECRET=Google Client
API_KEY
PHONE_NUMBER
DATABASE_URL=sqlite:///db.sqlite3  # or PostgreSQL
REDIS_URL=redis://localhost:6379/0
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

## Deployment

For production deployments, we recommend using:
- **Gunicorn** for the backend
- **NGINX** for request processing
- **Docker + Docker Compose** (optional)

---

## Contribution to the project
The project is open for contributions! To do this:
1. Create a repository.
2. Make changes in your branch.
3. Submit a pull request.

### Author: Pro100grammer

### License.
This project is distributed under the MIT license.

