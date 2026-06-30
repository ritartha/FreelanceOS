from django.db import transaction
from django.db.models import Sum

from apps.files.models import FileAttachment, FileVersion


@transaction.atomic
def upload_new_version(file_attachment: FileAttachment, new_file, user=None) -> FileVersion:
    """
    Archive the current file content as a FileVersion, then replace
    file_attachment.file with the new upload and bump current_version.
    """
    archived = FileVersion.objects.create(
        tenant=file_attachment.tenant,
        file_attachment=file_attachment,
        version_number=file_attachment.current_version,
        file=file_attachment.file,
        size=file_attachment.size,
        created_by=user,
    )

    file_attachment.file = new_file
    file_attachment.size = new_file.size
    file_attachment.current_version += 1
    file_attachment.save(update_fields=["file", "size", "current_version", "updated_at"])

    return archived


def get_tenant_storage_usage(tenant) -> dict:
    """
    Returns total bytes used by a tenant across current file content and
    archived versions, plus a per-folder breakdown for the top-level folders.
    """
    current_total = FileAttachment.objects.filter(tenant=tenant).aggregate(total=Sum("size"))["total"] or 0
    version_total = FileVersion.objects.filter(tenant=tenant).aggregate(total=Sum("size"))["total"] or 0

    from apps.files.models import Folder

    by_folder = []
    for folder in Folder.objects.filter(tenant=tenant, parent__isnull=True):
        folder_bytes = FileAttachment.objects.filter(tenant=tenant, folder=folder).aggregate(
            total=Sum("size")
        )["total"] or 0
        by_folder.append({"folder_id": str(folder.id), "name": folder.name, "bytes": folder_bytes})

    return {
        "total_bytes": current_total + version_total,
        "current_bytes": current_total,
        "version_bytes": version_total,
        "by_folder": by_folder,
    }
