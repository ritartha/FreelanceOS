from rest_framework import viewsets

from apps.common.mixins import TenantQuerysetMixin
from apps.notifications.api.serializers import NotificationSerializer
from apps.notifications.models import Notification


class NotificationViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Notification.all_objects.all()
    serializer_class = NotificationSerializer
