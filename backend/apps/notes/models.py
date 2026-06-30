"""
Notes app.

A Note attaches generically to any other model (Client, Project, Task, etc.)
via Django's ContentType framework, so adding "notes" support to a new app
later never requires a migration on this app or that one.

Usage from another app, e.g. attaching a note to a Project instance:

    from apps.notes.models import Note
    Note.objects.create(
        tenant=project.tenant,
        title="Kickoff call notes",
        body="- Discussed scope\n- Agreed on timeline",
        content_object=project,
        created_by=request.user,
    )

To fetch notes for an object:

    from django.contrib.contenttypes.models import ContentType
    Note.objects.filter(
        content_type=ContentType.objects.get_for_model(project),
        object_id=project.id,
    )
"""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.common.models import TenantAwareModel


class Note(TenantAwareModel):
    title = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True, help_text="Markdown content, including fenced code blocks.")
    is_pinned = models.BooleanField(default=False)

    # Generic attachment target — any tenant-scoped model can have notes.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.UUIDField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        db_table = "notes_note"
        ordering = ["-is_pinned", "-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return self.title or (self.body[:50] if self.body else "Untitled note")


class NoteAttachment(TenantAwareModel):
    """
    File attached to a note. Stores a reference rather than duplicating
    apps.files.File so the Files app remains the single source of truth
    for storage/versioning once Stage 3 lands.
    """

    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name="attachments")
    file_url = models.URLField()
    file_name = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "notes_attachment"

    def __str__(self):
        return self.file_name or self.file_url
