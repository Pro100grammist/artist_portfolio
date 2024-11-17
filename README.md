# Django Web Application

## Опис проекту

Цей проєкт є веб-додатком, побудованим на основі **Django 5.1**, з використанням REST API (**Django REST Framework**) для роботи з клієнтською частиною. Додаток підтримує асинхронну обробку запитів через **Django Channels** та асинхронні задачі за допомогою **Celery** і **Redis**. База даних — **PostgreSQL**, інтеграція з якою виконується через сучасний драйвер **psycopg**.

Основні функції:
- Асинхронна обробка запитів.
- Взаємодія через REST API.
- Робота з чергами завдань (email-розсилки, обробка даних).
- WebSocket з'єднання для реального часу.

---

## Встановлення та запуск

### 1. Попередні вимоги

Перед встановленням переконайтеся, що на вашій машині встановлено наступні компоненти:
- **Python 3.11+**
- **PostgreSQL**
- **Redis**
- **Node.js** (опціонально, для фронтенду, якщо є інтеграція)

### 2. Клонування репозиторію


git clone https://github.com/your_username/your_project.git
cd your_project

### 3. Налаштування середовища
Створіть файл .env для зберігання конфігурації. 

DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://user:password@localhost:5432/your_db
REDIS_URL=redis://localhost:6379/0

Встановіть залежності:
pip install -r requirements.txt

### 4. Міграція бази даних
Застосуйте міграції для бази даних:
python manage.py migrate

### 5. Запуск серверів
#### Запуск веб-сервера:
python manage.py runserver

#### Запуск Celery:
celery -A your_project worker --loglevel=info

#### Запуск Redis:
redis-server

#### Тестування
pytest

### Основні технології
- Django: Backend.
- Django REST Framework: Для побудови REST API.
- PostgreSQL: Реляційна база даних.
- Redis: Для кешування і черг задач.
- Celery: Асинхронні задачі.
- Django Channels: WebSocket та асинхронна обробка запитів.
- Gunicorn: Сервер для production.

### Внесок у проект
Ми відкриті до внесків! Для цього:
- Форкніть репозиторій.
- Зробіть зміни у своїй гілці.
- Відправте pull request.

### Автор: Pro100grammer

### Ліцензія
Цей проект розповсюджується під ліцензією MIT.