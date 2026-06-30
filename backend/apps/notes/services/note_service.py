from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from apps.notes.models import Note


def notes_for_object(tenant, obj):
    """Return all notes attached to a given model instance, newest/pinned first."""
    content_type = ContentType.objects.get_for_model(obj.__class__)
    return Note.objects.filter(tenant=tenant, content_type=content_type, object_id=obj.id)


def create_note_for_object(tenant, obj, title="", body="", user=None, is_pinned=False) -> Note:
    """Create a note attached to any tenant-aware model instance."""
    content_type = ContentType.objects.get_for_model(obj.__class__)
    return Note.objects.create(
        tenant=tenant,
        content_type=content_type,
        object_id=obj.id,
        title=title,
        body=body,
        is_pinned=is_pinned,
        created_by=user,
    )


def search_notes(tenant, query: str):
    """Simple title/body search, scoped to tenant."""
    if not query:
        return Note.objects.filter(tenant=tenant)
    return Note.objects.filter(tenant=tenant).filter(
        Q(title__icontains=query) | Q(body__icontains=query)
    )
