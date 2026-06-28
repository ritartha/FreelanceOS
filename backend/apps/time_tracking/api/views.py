from rest_framework import viewsets

from apps.common.mixins import TenantQuerysetMixin
from apps.time_tracking.api.serializers import TimeLogSerializer
from apps.time_tracking.models import TimeLog


class TimeLogViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = TimeLog.all_objects.all()
    serializer_class = TimeLogSerializer
