from django.db import models

from apps.common.models import TenantAwareModel


class Company(TenantAwareModel):
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=150, blank=True)
    website = models.URLField(blank=True)
    size = models.CharField(max_length=50, blank=True, help_text="e.g. '1-10', '11-50'")

    class Meta:
        db_table = "crm_company"

    def __str__(self):
        return self.name


class Tag(TenantAwareModel):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, blank=True, default="#6366f1")

    class Meta:
        db_table = "crm_tag"
        constraints = [models.UniqueConstraint(fields=["tenant", "name"], name="uniq_tenant_tag_name")]

    def __str__(self):
        return self.name


class Client(TenantAwareModel):
    class StatusChoices(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        LEAD = "lead", "Lead"

    class LeadStageChoices(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        QUALIFIED = "qualified", "Qualified"
        PROPOSAL_SENT = "proposal_sent", "Proposal Sent"
        WON = "won", "Won"
        LOST = "lost", "Lost"

    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    company = models.CharField(max_length=255, blank=True, help_text="Free-text fallback; prefer company_ref.")
    company_ref = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="clients"
    )
    website = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.LEAD)
    lead_stage = models.CharField(
        max_length=20, choices=LeadStageChoices.choices, default=LeadStageChoices.NEW, blank=True
    )
    lead_score = models.PositiveSmallIntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True, related_name="clients")

    class Meta:
        db_table = "crm_client"

    def __str__(self):
        return self.name


class Contact(TenantAwareModel):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="contacts")
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = "crm_contact"

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()


class CommunicationHistory(TenantAwareModel):
    class TypeChoices(models.TextChoices):
        EMAIL = "email", "Email"
        CALL = "call", "Call"
        MEETING = "meeting", "Meeting"
        NOTE = "note", "Note"

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="communications")
    contact = models.ForeignKey(
        Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name="communications"
    )
    type = models.CharField(max_length=20, choices=TypeChoices.choices, default=TypeChoices.NOTE)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)
    occurred_at = models.DateTimeField()

    class Meta:
        db_table = "crm_communication_history"
        ordering = ["-occurred_at"]

    def __str__(self):
        return f"{self.get_type_display()} with {self.client} on {self.occurred_at:%Y-%m-%d}"
