import uuid

from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    class ActionChoices(models.TextChoices):
        CREATE = "create", "Create"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"
        VIEW = "view", "View"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs")
    action = models.CharField(max_length=20, choices=ActionChoices.choices)
    entity_type = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=255)
    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_log"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} {self.entity_type}"
