import logging

from django.core.mail import EmailMessage
from django.utils import timezone

from apps.quotations.models import Quotation
from apps.quotations.services.pdf_service import render_quotation_pdf

logger = logging.getLogger(__name__)


def send_quotation_email(quotation: Quotation, recipient_email: str | None = None) -> None:
    recipient = recipient_email or quotation.client.email
    if not recipient:
        raise ValueError("No recipient email available for this quotation's client.")

    pdf_bytes = render_quotation_pdf(quotation)
    public_url = f"/public/quotations/{quotation.public_token}/"

    message = EmailMessage(
        subject=f"Quotation {quotation.quotation_number}",
        body=(
            f"Hi,\n\nPlease find attached quotation {quotation.quotation_number}.\n"
            f"You can also view and respond to it online at: {public_url}\n"
        ),
        to=[recipient],
    )
    message.attach(f"{quotation.quotation_number}.pdf", pdf_bytes, "application/pdf")
    message.send(fail_silently=False)

    quotation.status = Quotation.StatusChoices.SENT
    quotation.sent_at = timezone.now()
    quotation.save(update_fields=["status", "sent_at", "updated_at"])


def accept_quotation(quotation: Quotation) -> Quotation:
    quotation.status = Quotation.StatusChoices.ACCEPTED
    quotation.accepted_at = timezone.now()
    quotation.save(update_fields=["status", "accepted_at", "updated_at"])
    return quotation


def decline_quotation(quotation: Quotation) -> Quotation:
    quotation.status = Quotation.StatusChoices.DECLINED
    quotation.declined_at = timezone.now()
    quotation.save(update_fields=["status", "declined_at", "updated_at"])
    return quotation
