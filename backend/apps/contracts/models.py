from django.db import models

from apps.common.models import TenantAwareModel


class Contract(TenantAwareModel):
    class StatusChoices(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        SIGNED = "signed", "Signed"
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"
        RENEWED = "renewed", "Renewed"

    client = models.ForeignKey("crm.Client", on_delete=models.CASCADE, related_name="contracts")
    project = models.ForeignKey(
        "projects.Project", on_delete=models.SET_NULL, null=True, blank=True, related_name="contracts"
    )
    quotation = models.ForeignKey(
        "quotations.Quotation", on_delete=models.SET_NULL, null=True, blank=True, related_name="contracts"
    )

    title = models.CharField(max_length=255)
    body_markdown = models.TextField(blank=True, help_text="Contract content in markdown.")
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.DRAFT)

    # Dates
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True, help_text="Leave blank for open-ended contracts.")
    signed_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    # Renewal / expiry reminder (Celery beat tasks read these)
    renewal_reminder_days = models.PositiveSmallIntegerField(
        default=30,
        help_text="Send renewal reminder this many days before end_date.",
    )
    expiry_reminder_sent = models.BooleanField(default=False)
    renewal_reminder_sent = models.BooleanField(default=False)

    # Signature storage — storing the uploaded signed file or a base64 sig image.
    # E-sign integration (DocuSign / HelloSign) is a future phase; for now
    # the freelancer uploads the signed PDF/image they receive back.
    signed_file = models.FileField(
        upload_to="contracts/signed/", null=True, blank=True,
        help_text="Upload the signed contract file received back from the client."
    )
    client_signature_name = models.CharField(
        max_length=255, blank=True,
        help_text="Name the client typed when signing (for lightweight in-app signature)."
    )

    notes = models.TextField(blank=True)

    class Meta:
        db_table = "contracts_contract"

    def __str__(self):
        return self.title

    @property
    def is_expiring_soon(self) -> bool:
        """True if the contract ends within renewal_reminder_days from today."""
        if not self.end_date:
            return False
        from django.utils import timezone
        from datetime import timedelta
        return self.end_date <= (timezone.now().date() + timedelta(days=self.renewal_reminder_days))


class ContractVersion(TenantAwareModel):
    """
    Immutable snapshot of a contract body, written whenever a signed/active
    contract is edited. Mirrors QuotationVersion's pattern.
    """

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveIntegerField()
    body_markdown = models.TextField(blank=True)

    class Meta:
        db_table = "contracts_version"
        ordering = ["-version_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["contract", "version_number"], name="uniq_contract_version_number"
            )
        ]

    def __str__(self):
        return f"{self.contract.title} v{self.version_number}"
