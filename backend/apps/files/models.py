import uuid

from django.db import models

from apps.common.models import TenantAwareModel


class FileAttachment(TenantAwareModel):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="attachments/")
    content_type = models.CharField(max_length=255, blank=True)
    size = models.PositiveBigIntegerField(default=0)
    entity_type = models.CharField(max_length=100)
    entity_id = models.UUIDField(default=uuid.uuid4)

    class Meta:
        db_table = "files_attachment"

    def __str__(self):
        return self.name
