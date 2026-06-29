import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create a superuser from environment variables if none exists."

    def handle(self, *args, **options):
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        first_name = os.environ.get("DJANGO_SUPERUSER_FIRST_NAME", "Admin")
        last_name = os.environ.get("DJANGO_SUPERUSER_LAST_NAME", "User")

        if not email or not password:
            self.stdout.write(
                self.style.WARNING("DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD env vars not set. Skipping.")
            )
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.SUCCESS(f"Superuser {email} already exists. Skipping."))
            return

        user_kwargs = {
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
        }
        User.objects.create_superuser(**user_kwargs)
        self.stdout.write(self.style.SUCCESS(f"Superuser {email} created successfully."))
