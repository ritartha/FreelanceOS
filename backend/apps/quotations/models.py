import uuid

from django.db import models

from apps.common.models import TenantAwareModel


class Quotation(TenantAwareModel):
    class StatusChoices(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        VIEWED = "viewed", "Viewed"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        EXPIRED = "expired", "Expired"
        CONVERTED = "converted", "Converted to Invoice"

    client = models.ForeignKey("crm.Client", on_delete=models.CASCADE, related_name="quotations")
    proposal = models.ForeignKey(
        "proposals.Proposal", on_delete=models.SET_NULL, null=True, blank=True, related_name="quotations"
    )
    quotation_number = models.CharField(max_length=100, blank=True)  # auto-generated if not provided
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.DRAFT)
    issue_date = models.DateField()
    valid_until = models.DateField(null=True, blank=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_type = models.CharField(
        max_length=10,
        choices=[("flat", "Flat"), ("percent", "Percent")],
        default="percent",
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    gst_number = models.CharField(max_length=30, blank=True, help_text="Client/business GSTIN, if applicable.")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="GST/tax %.")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="USD")
    notes = models.TextField(blank=True)

    public_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "quotations_quotation"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "quotation_number"], name="uniq_quotation_number_per_tenant")
        ]

    def __str__(self):
        return self.quotation_number or f"Quotation for {self.client}"

    @classmethod
    def generate_quotation_number(cls, tenant):
        """Generate the next sequential quotation number, e.g. QUO-0001. Mirrors Invoice.generate_invoice_number."""
        last = (
            cls.all_objects.filter(tenant=tenant, quotation_number__startswith="QUO-")
            .order_by("-quotation_number")
            .values_list("quotation_number", flat=True)
            .first()
        )
        if last:
            try:
                num = int(last.split("-")[-1]) + 1
            except (ValueError, IndexError):
                num = 1
        else:
            num = 1
        return f"QUO-{num:04d}"


class QuotationLineItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name="line_items")
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = "quotations_line_item"

    def __str__(self):
        return self.description


class QuotationVersion(TenantAwareModel):
    """
    Immutable snapshot of a quotation, written whenever a sent quotation is
    edited (sent quotations shouldn't be silently mutated — see
    services/quotation_service.py revise_quotation()).
    """

    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveIntegerField()
    snapshot = models.JSONField(help_text="Serialized quotation + line items at the time of this version.")

    class Meta:
        db_table = "quotations_version"
        ordering = ["-version_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["quotation", "version_number"], name="uniq_quotation_version_number"
            )
        ]

    def __str__(self):
        return f"{self.quotation} v{self.version_number}"
