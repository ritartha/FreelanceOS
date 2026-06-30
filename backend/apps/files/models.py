import uuid

from django.db import models

from apps.common.models import TenantAwareModel


class Folder(TenantAwareModel):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="subfolders"
    )
    # Optional scoping to a CRM/Project/etc. entity, mirroring FileAttachment's
    # existing entity_type/entity_id convention rather than introducing a
    # second generic-attachment pattern.
    entity_type = models.CharField(max_length=100, blank=True)
    entity_id = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "files_folder"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "parent", "name"], name="uniq_tenant_parent_folder_name")
        ]

    def __str__(self):
        return self.name


class FileTag(TenantAwareModel):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, blank=True, default="#6366f1")

    class Meta:
        db_table = "files_tag"
        constraints = [models.UniqueConstraint(fields=["tenant", "name"], name="uniq_tenant_filetag_name")]

    def __str__(self):
        return self.name


class FileAttachment(TenantAwareModel):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="attachments/")
    content_type = models.CharField(max_length=255, blank=True)
    size = models.PositiveBigIntegerField(default=0)
    entity_type = models.CharField(max_length=100)
    entity_id = models.UUIDField(default=uuid.uuid4)
    folder = models.ForeignKey(
        Folder, on_delete=models.SET_NULL, null=True, blank=True, related_name="files"
    )
    tags = models.ManyToManyField(FileTag, blank=True, related_name="files")
    current_version = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "files_attachment"

    def __str__(self):
        return self.name


class FileVersion(TenantAwareModel):
    """
    Snapshot of a FileAttachment at a point in time. Created automatically
    whenever a file is re-uploaded over an existing FileAttachment (see
    apps.files.services.file_service.upload_new_version).
    """

    file_attachment = models.ForeignKey(FileAttachment, on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveIntegerField()
    file = models.FileField(upload_to="attachments/versions/")
    size = models.PositiveBigIntegerField(default=0)

    class Meta:
        db_table = "files_version"
        ordering = ["-version_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["file_attachment", "version_number"], name="uniq_file_version_number"
            )
        ]

    def __str__(self):
        return f"{self.file_attachment.name} v{self.version_number}"
