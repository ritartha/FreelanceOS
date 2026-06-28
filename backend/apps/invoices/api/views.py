from rest_framework import viewsets

from apps.common.mixins import TenantQuerysetMixin
from apps.invoices.api.serializers import InvoiceLineItemSerializer, InvoiceSerializer
from apps.invoices.models import Invoice, InvoiceLineItem


class InvoiceViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Invoice.all_objects.all()
    serializer_class = InvoiceSerializer


class InvoiceLineItemViewSet(viewsets.ModelViewSet):
    queryset = InvoiceLineItem.objects.all()
    serializer_class = InvoiceLineItemSerializer
