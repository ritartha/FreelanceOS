import logging

from celery import shared_task
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


@shared_task
def send_verification_email_task(user_id, token):
    user = get_user_model().objects.filter(id=user_id).first()
    if not user:
        return
    logger.info("Verification email task queued for %s with token %s", user.email, token)
