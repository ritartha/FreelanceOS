from rest_framework import viewsets

from apps.common.mixins import TenantQuerysetMixin
from apps.crm.api.serializers import ClientSerializer, ContactSerializer
from apps.crm.models import Client, Contact


class ClientViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class ContactViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
