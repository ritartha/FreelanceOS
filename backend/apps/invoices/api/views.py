from rest_framework import viewsets

from apps.common.exceptions import TenantRequiredError
from apps.common.mixins import TenantQuerysetMixin
from apps.invoices.api.serializers import InvoiceLineItemSerializer, InvoiceSerializer
from apps.invoices.models import Invoice, InvoiceLineItem


class InvoiceViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Invoice.all_objects.all()
    serializer_class = InvoiceSerializer


class InvoiceLineItemViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceLineItemSerializer

    def _get_tenant(self):
        tenant = getattr(self.request, "tenant", None)
        if tenant:
            return tenant
        if self.request.user and self.request.user.is_authenticated:
            from apps.tenants.models import Membership
            membership = Membership.objects.filter(
                user=self.request.user,
                status="active",
                tenant__is_active=True,
            ).order_by("-created_at").first()
            if membership:
                self.request.tenant = membership.tenant
                return membership.tenant
        return None

    def get_queryset(self):
        tenant = self._get_tenant()
        if not tenant:
            raise TenantRequiredError()
        return InvoiceLineItem.objects.filter(invoice__tenant=tenant)
