from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.mixins import TenantQuerysetMixin
from apps.crm.api.serializers import (
    ClientSerializer,
    CommunicationHistorySerializer,
    CompanySerializer,
    ContactSerializer,
    TagSerializer,
)
from apps.crm.models import Client, CommunicationHistory, Company, Contact, Tag
from apps.crm.services.lead_service import advance_lead_stage


class ClientViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(email__icontains=search)
                | Q(company__icontains=search)
            )

        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        lead_stage = self.request.query_params.get("lead_stage")
        if lead_stage:
            qs = qs.filter(lead_stage=lead_stage)

        tag = self.request.query_params.get("tag")
        if tag:
            qs = qs.filter(tags__name=tag)

        return qs.distinct()

    @action(detail=True, methods=["post"], url_path="advance-stage")
    def advance_stage(self, request, pk=None):
        client = self.get_object()
        new_stage = request.data.get("lead_stage")
        if not new_stage:
            return Response({"detail": "lead_stage is required."}, status=400)
        client = advance_lead_stage(client, new_stage, user=request.user)
        return Response(self.get_serializer(client).data)


class ContactViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


class CompanyViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class TagViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class CommunicationHistoryViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = CommunicationHistory.objects.all()
    serializer_class = CommunicationHistorySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        client_id = self.request.query_params.get("client")
        if client_id:
            qs = qs.filter(client_id=client_id)
        return qs
