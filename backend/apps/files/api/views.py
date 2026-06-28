from rest_framework import viewsets

from apps.common.mixins import TenantQuerysetMixin
from apps.files.api.serializers import FileAttachmentSerializer
from apps.files.models import FileAttachment


class FileAttachmentViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = FileAttachment.all_objects.all()
    serializer_class = FileAttachmentSerializer
