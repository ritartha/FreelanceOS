import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def send_proposal_email_task(proposal_id, recipient_email=None):
    from apps.proposals.models import Proposal
    from apps.proposals.services.proposal_service import send_proposal_email

    proposal = Proposal.objects.filter(id=proposal_id).first()
    if not proposal:
        logger.warning("send_proposal_email_task: Proposal %s not found", proposal_id)
        return

    try:
        send_proposal_email(proposal, recipient_email=recipient_email)
    except Exception:
        logger.exception("Failed to send proposal email for %s", proposal_id)
        raise
