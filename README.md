
# Ecommerce Backend (Django)

This is a ready-to-run Django backend for the E-Commerce mini project described in the assignment.

How to run (locally):

1. Create a virtualenv and activate it.
2. Install requirements:
   pip install -r requirements.txt
3. Copy .env.example to .env and adjust if needed.
4. Run migrations:
   python manage.py makemigrations
   python manage.py migrate
5. Seed data:
   python manage.py seed_data
6. Run server:
   python manage.py runserver

API base: /api/
Admin site: /admin-django/
Default seeded admin: admin@example.com / Admin@12345
