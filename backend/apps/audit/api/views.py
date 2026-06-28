from rest_framework import viewsets

from apps.audit.api.serializers import AuditLogSerializer
from apps.audit.models import AuditLog


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
