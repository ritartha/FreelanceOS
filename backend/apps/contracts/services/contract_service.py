from django.db import transaction
from django.utils import timezone

from apps.contracts.models import Contract, ContractVersion


@transaction.atomic
def sign_contract(contract: Contract, signed_file=None, client_signature_name: str = "", user=None) -> Contract:
    """
    Mark a contract as signed. Accepts either an uploaded signed file or a
    client_signature_name string (lightweight "type your name" e-sign).
    """
    if signed_file:
        contract.signed_file = signed_file
    if client_signature_name:
        contract.client_signature_name = client_signature_name

    contract.status = Contract.StatusChoices.SIGNED
    contract.signed_at = timezone.now()
    contract.save(update_fields=["signed_file", "client_signature_name", "status", "signed_at", "updated_at"])
    return contract


@transaction.atomic
def activate_contract(contract: Contract) -> Contract:
    contract.status = Contract.StatusChoices.ACTIVE
    contract.save(update_fields=["status", "updated_at"])
    return contract


@transaction.atomic
def snapshot_version(contract: Contract, user=None) -> ContractVersion:
    """Snapshot the current body before overwriting it."""
    next_version = contract.versions.count() + 1
    return ContractVersion.objects.create(
        tenant=contract.tenant,
        contract=contract,
        version_number=next_version,
        body_markdown=contract.body_markdown,
        created_by=user,
    )
