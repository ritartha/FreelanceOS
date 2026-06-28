from rest_framework import viewsets

from apps.tenants.api.serializers import MembershipSerializer, RoleSerializer, TenantSerializer
from apps.tenants.models import Membership, Role, Tenant


class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
