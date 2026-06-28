from django.conf import settings
from django.db import models

from apps.common.models import TenantAwareModel


class TimeLog(TenantAwareModel):
    task = models.ForeignKey("tasks.Task", on_delete=models.SET_NULL, null=True, blank=True, related_name="time_logs")
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="time_logs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="time_logs")
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    is_billable = models.BooleanField(default=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = "time_tracking_timelog"

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time and self.end_time >= self.start_time:
            self.duration_seconds = int((self.end_time - self.start_time).total_seconds())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project} - {self.user}"
