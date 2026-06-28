from django.db import models

from apps.common.models import TenantAwareModel


class Project(TenantAwareModel):
    class StatusChoices(models.TextChoices):
        PLANNING = "planning", "Planning"
        ACTIVE = "active", "Active"
        ON_HOLD = "on_hold", "On Hold"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    name = models.CharField(max_length=255)
    client = models.ForeignKey("crm.Client", on_delete=models.SET_NULL, null=True, blank=True, related_name="projects")
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PLANNING)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="USD")
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = "projects_project"

    def __str__(self):
        return self.name
