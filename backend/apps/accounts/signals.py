from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import User
from apps.accounts.tasks import send_verification_email_task
from apps.accounts.services.token_service import generate_verification_token


@receiver(post_save, sender=User)
def send_verification_email_on_user_create(sender, instance, created, **kwargs):
    if created and not instance.is_email_verified:
        token = generate_verification_token(instance)
        send_verification_email_task.delay(str(instance.id), token)
