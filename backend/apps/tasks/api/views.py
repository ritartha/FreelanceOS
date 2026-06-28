from rest_framework import viewsets

from apps.common.mixins import TenantQuerysetMixin
from apps.tasks.api.serializers import TaskSerializer
from apps.tasks.models import Task


class TaskViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Task.all_objects.all()
    serializer_class = TaskSerializer
