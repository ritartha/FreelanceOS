from django.db import models

from apps.common.models import TenantAwareModel


class Client(TenantAwareModel):
    class StatusChoices(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        LEAD = "lead", "Lead"

    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    company = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.LEAD)

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
