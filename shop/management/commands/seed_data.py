
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from shop.models import Product
User = get_user_model()
class Command(BaseCommand):
    help = "Seed database with admin user and sample products"
    def handle(self, *args, **options):
        admin_email = "admin@example.com"
        admin_password = "Admin@12345"
        if not User.objects.filter(email=admin_email).exists():
            user = User.objects.create(email=admin_email, username="admin", role="admin", is_staff=True, is_superuser=False)
            user.set_password(admin_password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created admin {admin_email} / {admin_password}"))
        else:
            self.stdout.write("Admin already exists.")
        sample_products = [
            {"name": "Sample Phone X", "price": 299.99, "stock": 50, "category": "Electronics", "description": "A sample smartphone."},
            {"name": "Coffee Mug", "price": 9.99, "stock": 200, "category": "Home", "description": "Ceramic mug."},
            {"name": "Running Shoes", "price": 79.99, "stock": 120, "category": "Apparel", "description": "Comfortable shoes."},
        ]
        for p in sample_products:
            if not Product.objects.filter(name=p["name"]).exists():
                Product.objects.create(**p)
                self.stdout.write(self.style.SUCCESS(f"Created product {p['name']}"))
        self.stdout.write(self.style.SUCCESS("Seeding complete."))
