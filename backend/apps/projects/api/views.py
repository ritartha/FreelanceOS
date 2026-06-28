from rest_framework import viewsets

from apps.common.mixins import TenantQuerysetMixin
from apps.projects.api.serializers import ProjectSerializer
from apps.projects.models import Project


class ProjectViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Project.all_objects.all()
    serializer_class = ProjectSerializer
