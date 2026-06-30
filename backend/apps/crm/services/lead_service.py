"""
CRM business logic: lead scoring and lead-stage transitions.

Score is a simple weighted heuristic (0-100, clamped) based on signals
already on the model — engagement (communication count), profile
completeness, and stage. Swap the weights below as the product evolves;
keeping this in one function means there's a single place to tune it.
"""

from django.db import transaction
from django.utils import timezone

from apps.crm.models import Client


SCORE_WEIGHTS = {
    "has_email": 10,
    "has_phone": 5,
    "has_company": 10,
    "per_communication": 5,
    "max_communication_points": 30,
    "stage_points": {
        Client.LeadStageChoices.NEW: 0,
        Client.LeadStageChoices.CONTACTED: 10,
        Client.LeadStageChoices.QUALIFIED: 25,
        Client.LeadStageChoices.PROPOSAL_SENT: 40,
        Client.LeadStageChoices.WON: 100,
        Client.LeadStageChoices.LOST: 0,
    },
}


def recalculate_lead_score(client: Client) -> int:
    """Recompute and persist client.lead_score. Returns the new score."""
    score = 0
    if client.email:
        score += SCORE_WEIGHTS["has_email"]
    if client.phone:
        score += SCORE_WEIGHTS["has_phone"]
    if client.company or client.company_ref_id:
        score += SCORE_WEIGHTS["has_company"]

    comm_count = client.communications.count()
    score += min(
        comm_count * SCORE_WEIGHTS["per_communication"],
        SCORE_WEIGHTS["max_communication_points"],
    )

    score += SCORE_WEIGHTS["stage_points"].get(client.lead_stage, 0)

    score = max(0, min(score, 100))

    if score != client.lead_score:
        client.lead_score = score
        client.save(update_fields=["lead_score", "updated_at"])

    return score


@transaction.atomic
def advance_lead_stage(client: Client, new_stage: str, user=None) -> Client:
    """
    Move a client to a new lead stage, logging the transition as a
    CommunicationHistory note, and recalculate the score afterward.
    """
    from apps.crm.models import CommunicationHistory

    if new_stage not in Client.LeadStageChoices.values:
        raise ValueError(f"Invalid lead stage: {new_stage}")

    old_stage = client.lead_stage
    client.lead_stage = new_stage

    if new_stage == Client.LeadStageChoices.WON:
        client.status = Client.StatusChoices.ACTIVE
    elif new_stage == Client.LeadStageChoices.LOST:
        client.status = Client.StatusChoices.INACTIVE

    client.save(update_fields=["lead_stage", "status", "updated_at"])

    CommunicationHistory.objects.create(
        tenant=client.tenant,
        client=client,
        type=CommunicationHistory.TypeChoices.NOTE,
        subject="Lead stage changed",
        body=f"Stage changed from '{old_stage}' to '{new_stage}'.",
        occurred_at=timezone.now(),
        created_by=user,
    )

    recalculate_lead_score(client)
    return client
