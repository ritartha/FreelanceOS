from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.mixins import TenantQuerysetMixin
from apps.files.api.serializers import (
    FileAttachmentSerializer,
    FileTagSerializer,
    FileVersionSerializer,
    FolderSerializer,
)
from apps.files.models import FileAttachment, FileTag, FileVersion, Folder
from apps.files.services.file_service import get_tenant_storage_usage, upload_new_version


class FolderViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        parent = self.request.query_params.get("parent")
        if parent == "root":
            qs = qs.filter(parent__isnull=True)
        elif parent:
            qs = qs.filter(parent_id=parent)
        return qs


class FileTagViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = FileTag.objects.all()
    serializer_class = FileTagSerializer


class FileAttachmentViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = FileAttachment.all_objects.all()
    serializer_class = FileAttachmentSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(name__icontains=search))

        folder = self.request.query_params.get("folder")
        if folder:
            qs = qs.filter(folder_id=folder)

        tag = self.request.query_params.get("tag")
        if tag:
            qs = qs.filter(tags__name=tag)

        entity_type = self.request.query_params.get("entity_type")
        entity_id = self.request.query_params.get("entity_id")
        if entity_type and entity_id:
            qs = qs.filter(entity_type=entity_type, entity_id=entity_id)

        return qs.distinct()

    def perform_create(self, serializer):
        tenant = self._resolve_tenant()
        uploaded_file = self.request.FILES.get("file")
        size = uploaded_file.size if uploaded_file else 0
        serializer.save(tenant=tenant, created_by=self.request.user, size=size)

    @action(detail=True, methods=["post"], url_path="new-version")
    def new_version(self, request, pk=None):
        file_attachment = self.get_object()
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"detail": "file is required."}, status=400)
        archived = upload_new_version(file_attachment, uploaded_file, user=request.user)
        return Response(
            {
                "archived_version": FileVersionSerializer(archived).data,
                "file": FileAttachmentSerializer(file_attachment).data,
            }
        )

    @action(detail=False, methods=["get"], url_path="storage-usage")
    def storage_usage(self, request):
        tenant = self._resolve_tenant()
        return Response(get_tenant_storage_usage(tenant))
