import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def check_contract_reminders():
    """
    Daily task (scheduled via Celery beat) that scans active contracts and
    sends renewal/expiry reminder emails.

    Add to settings:
        CELERY_BEAT_SCHEDULE = {
            ...
            "contract-reminders-daily": {
                "task": "apps.contracts.tasks.check_contract_reminders",
                "schedule": crontab(hour=8, minute=0),  # 8 AM UTC daily
            },
        }
    """
    from apps.contracts.models import Contract

    today = timezone.now().date()
    active_contracts = Contract.objects.filter(
        status__in=[Contract.StatusChoices.ACTIVE, Contract.StatusChoices.SIGNED],
        end_date__isnull=False,
        is_deleted=False,
    )

    for contract in active_contracts:
        days_until_expiry = (contract.end_date - today).days

        # Expiry alert: contract ends today or is already past
        if days_until_expiry <= 0 and not contract.expiry_reminder_sent:
            send_contract_expiry_alert.delay(str(contract.id))

        # Renewal reminder: within the configured window
        elif days_until_expiry <= contract.renewal_reminder_days and not contract.renewal_reminder_sent:
            send_contract_renewal_reminder.delay(str(contract.id))


@shared_task
def send_contract_expiry_alert(contract_id: str):
    from django.core.mail import EmailMessage

    from apps.contracts.models import Contract

    contract = Contract.objects.select_related("client", "tenant").filter(id=contract_id).first()
    if not contract:
        logger.warning("send_contract_expiry_alert: Contract %s not found", contract_id)
        return

    # Notify the tenant owner (freelancer)
    owner_email = getattr(contract.created_by, "email", None)
    if owner_email:
        EmailMessage(
            subject=f"[FreelanceOS] Contract expired: {contract.title}",
            body=(
                f"Your contract \"{contract.title}\" with {contract.client} "
                f"expired on {contract.end_date}.\n\n"
                f"Log in to review or renew it."
            ),
            to=[owner_email],
        ).send(fail_silently=True)

    contract.expiry_reminder_sent = True
    contract.status = Contract.StatusChoices.EXPIRED
    contract.save(update_fields=["expiry_reminder_sent", "status", "updated_at"])


@shared_task
def send_contract_renewal_reminder(contract_id: str):
    from django.core.mail import EmailMessage

    from apps.contracts.models import Contract

    contract = Contract.objects.select_related("client", "tenant").filter(id=contract_id).first()
    if not contract:
        logger.warning("send_contract_renewal_reminder: Contract %s not found", contract_id)
        return

    owner_email = getattr(contract.created_by, "email", None)
    if owner_email:
        EmailMessage(
            subject=f"[FreelanceOS] Contract renewal reminder: {contract.title}",
            body=(
                f"Your contract \"{contract.title}\" with {contract.client} "
                f"expires on {contract.end_date} "
                f"({(contract.end_date - timezone.now().date()).days} days away).\n\n"
                f"Log in to renew it before it expires."
            ),
            to=[owner_email],
        ).send(fail_silently=True)

    contract.renewal_reminder_sent = True
    contract.save(update_fields=["renewal_reminder_sent", "updated_at"])
