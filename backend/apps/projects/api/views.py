from rest_framework import viewsets

from apps.common.mixins import TenantQuerysetMixin
from apps.projects.api.serializers import ProjectSerializer
from apps.projects.models import Project


class ProjectViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
<<<<<<< Updated upstream
    queryset = Project.objects.all()  # uses TenantAwareManager which filters is_deleted=False
=======
    queryset = Project.objects.all()
>>>>>>> Stashed changes
    serializer_class = ProjectSerializer
