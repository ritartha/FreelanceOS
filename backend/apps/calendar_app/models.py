from django.db import models

from apps.common.models import TenantAwareModel


class CalendarEvent(TenantAwareModel):
    class EventTypeChoices(models.TextChoices):
        TASK_DEADLINE = "task_deadline", "Task Deadline"
        PROJECT_DEADLINE = "project_deadline", "Project Deadline"
        INVOICE_DUE = "invoice_due", "Invoice Due"
        CONTRACT_EXPIRY = "contract_expiry", "Contract Expiry"
        MANUAL = "manual", "Manual"

    title = models.CharField(max_length=255)
    event_type = models.CharField(
        max_length=30,
        choices=EventTypeChoices.choices,
        default=EventTypeChoices.MANUAL,
    )
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    all_day = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calendar_events",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calendar_events",
    )
    invoice = models.ForeignKey(
        "invoices.Invoice",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calendar_events",
    )
    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calendar_events",
    )
    google_event_id = models.CharField(max_length=255, blank=True)
    google_calendar_id = models.CharField(max_length=255, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "calendar_event"
        ordering = ["start"]

    def __str__(self):
        return self.title
