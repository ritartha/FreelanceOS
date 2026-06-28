from django.conf import settings
from django.db import models

from apps.common.models import TenantAwareModel


class Task(TenantAwareModel):
    class StatusChoices(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        REVIEW = "review", "Review"
        DONE = "done", "Done"
        CANCELLED = "cancelled", "Cancelled"

    class PriorityChoices(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.TODO)
    priority = models.CharField(max_length=20, choices=PriorityChoices.choices, default=PriorityChoices.MEDIUM)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tasks")
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    actual_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        db_table = "tasks_task"

    def __str__(self):
        return self.title
