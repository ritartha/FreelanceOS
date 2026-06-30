from django.apps import apps as django_apps
from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.common.mixins import TenantQuerysetMixin
from apps.notes.api.serializers import NoteAttachmentSerializer, NoteSerializer
from apps.notes.models import Note, NoteAttachment
from apps.notes.services.note_service import search_notes


class NoteViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    """
    Notes can be filtered by the object they're attached to via query params:
        GET /api/v1/notes/?object_type=crm.client&object_id=<uuid>
    Or searched:
        GET /api/v1/notes/?search=kickoff
    To attach a note when creating, pass object_type ("app_label.model") and
    object_id in the POST body instead of raw content_type/object_id.
    """

    queryset = Note.objects.all()
    serializer_class = NoteSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        search = self.request.query_params.get("search")
        if search:
            qs = search_notes(self._resolve_tenant(), search)

        object_type = self.request.query_params.get("object_type")
        object_id = self.request.query_params.get("object_id")
        if object_type and object_id:
            try:
                app_label, model = object_type.split(".")
                content_type = ContentType.objects.get(app_label=app_label, model=model)
            except (ValueError, ContentType.DoesNotExist):
                raise ValidationError({"object_type": "Invalid format. Use 'app_label.model'."})
            qs = qs.filter(content_type=content_type, object_id=object_id)

        return qs

    def perform_create(self, serializer):
        tenant = self._resolve_tenant()
        object_type = self.request.data.get("object_type")
        object_id = self.request.data.get("object_id")

        content_type = None
        if object_type:
            try:
                app_label, model = object_type.split(".")
                content_type = ContentType.objects.get(app_label=app_label, model=model)
                django_apps.get_model(app_label, model)  # validates it's a real model
            except (ValueError, LookupError, ContentType.DoesNotExist):
                raise ValidationError({"object_type": "Invalid format. Use 'app_label.model'."})

        serializer.save(
            tenant=tenant,
            created_by=self.request.user,
            content_type=content_type,
            object_id=object_id or None,
        )


class NoteAttachmentViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = NoteAttachment.objects.all()
    serializer_class = NoteAttachmentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        note_id = self.request.query_params.get("note")
        if note_id:
            qs = qs.filter(note_id=note_id)
        return qs
