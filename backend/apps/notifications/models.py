from django.conf import settings
from django.db import models

from apps.common.models import TenantAwareModel


class Notification(TenantAwareModel):
    class TypeChoices(models.TextChoices):
        INFO = "info", "Info"
        WARNING = "warning", "Warning"
        SUCCESS = "success", "Success"
        ERROR = "error", "Error"

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    body = models.TextField()
    type = models.CharField(max_length=20, choices=TypeChoices.choices, default=TypeChoices.INFO)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    link = models.URLField(blank=True)

    class Meta:
        db_table = "notifications_notification"

    def __str__(self):
        return self.title
