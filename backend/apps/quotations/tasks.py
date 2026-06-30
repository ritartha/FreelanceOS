import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def send_quotation_email_task(quotation_id, recipient_email=None):
    from apps.quotations.models import Quotation
    from apps.quotations.services.email_service import send_quotation_email

    quotation = Quotation.objects.filter(id=quotation_id).first()
    if not quotation:
        logger.warning("send_quotation_email_task: Quotation %s not found", quotation_id)
        return

    try:
        send_quotation_email(quotation, recipient_email=recipient_email)
    except Exception:
        logger.exception("Failed to send quotation email for %s", quotation_id)
        raise
