from rest_framework import viewsets

from apps.audit.api.serializers import AuditLogSerializer
from apps.audit.models import AuditLog


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if tenant:
            return AuditLog.objects.filter(tenant=tenant)
        return AuditLog.objects.none()
