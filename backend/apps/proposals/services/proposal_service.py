import logging

from django.core.mail import EmailMessage
from django.utils import timezone

from apps.proposals.models import Proposal
from apps.proposals.services.pdf_service import render_proposal_pdf

logger = logging.getLogger(__name__)


def send_proposal_email(proposal: Proposal, recipient_email: str | None = None) -> None:
    """
    Emails the proposal as a PDF attachment plus a link to the public
    acceptance page, and marks it as sent.
    """
    recipient = recipient_email or proposal.client.email
    if not recipient:
        raise ValueError("No recipient email available for this proposal's client.")

    pdf_bytes = render_proposal_pdf(proposal)
    public_url = f"/public/proposals/{proposal.public_token}/"

    message = EmailMessage(
        subject=f"Proposal: {proposal.title}",
        body=(
            f"Hi,\n\nPlease find attached the proposal \"{proposal.title}\".\n"
            f"You can also view and respond to it online at: {public_url}\n"
        ),
        to=[recipient],
    )
    message.attach(f"{proposal.title}.pdf", pdf_bytes, "application/pdf")
    message.send(fail_silently=False)

    proposal.status = Proposal.StatusChoices.SENT
    proposal.sent_at = timezone.now()
    proposal.save(update_fields=["status", "sent_at", "updated_at"])


def record_view(proposal: Proposal, ip_address: str | None = None, user_agent: str = "") -> None:
    """Logs a public view and flips status draft/sent -> viewed (idempotent past that point)."""
    from apps.proposals.models import ProposalView

    ProposalView.objects.create(
        tenant=proposal.tenant,
        proposal=proposal,
        ip_address=ip_address,
        user_agent=user_agent[:500],
    )

    if proposal.status in (Proposal.StatusChoices.SENT,):
        proposal.status = Proposal.StatusChoices.VIEWED
        proposal.save(update_fields=["status", "updated_at"])


def accept_proposal(proposal: Proposal) -> Proposal:
    proposal.status = Proposal.StatusChoices.ACCEPTED
    proposal.accepted_at = timezone.now()
    proposal.save(update_fields=["status", "accepted_at", "updated_at"])
    return proposal


def decline_proposal(proposal: Proposal) -> Proposal:
    proposal.status = Proposal.StatusChoices.DECLINED
    proposal.declined_at = timezone.now()
    proposal.save(update_fields=["status", "declined_at", "updated_at"])
    return proposal
