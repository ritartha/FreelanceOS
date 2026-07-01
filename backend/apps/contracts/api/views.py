from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.mixins import TenantQuerysetMixin
from apps.contracts.api.serializers import ContractSerializer, ContractVersionSerializer
from apps.contracts.models import Contract
from apps.contracts.services.contract_service import activate_contract, sign_contract, snapshot_version
from apps.contracts.services.pdf_service import render_contract_pdf


class ContractViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        client_id = self.request.query_params.get("client")
        if client_id:
            qs = qs.filter(client_id=client_id)
        project_id = self.request.query_params.get("project")
        if project_id:
            qs = qs.filter(project_id=project_id)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        expiring = self.request.query_params.get("expiring_soon")
        if expiring and expiring.lower() == "true":
            qs = [c for c in qs if c.is_expiring_soon]
        return qs

    def perform_create(self, serializer):
        tenant = self._resolve_tenant()
        serializer.save(tenant=tenant, created_by=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        # Snapshot before editing any non-draft contract
        if instance.status != Contract.StatusChoices.DRAFT:
            snapshot_version(instance, user=self.request.user)
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="sign")
    def sign(self, request, pk=None):
        contract = self.get_object()
        signed_file = request.FILES.get("signed_file")
        signature_name = request.data.get("client_signature_name", "")
        if not signed_file and not signature_name:
            return Response({"detail": "Provide either signed_file or client_signature_name."}, status=400)
        contract = sign_contract(
            contract,
            signed_file=signed_file,
            client_signature_name=signature_name,
            user=request.user,
        )
        return Response(ContractSerializer(contract).data)

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        contract = self.get_object()
        contract = activate_contract(contract)
        return Response(ContractSerializer(contract).data)

    @action(detail=True, methods=["get"], url_path="pdf")
    def pdf(self, request, pk=None):
        contract = self.get_object()
        pdf_bytes = render_contract_pdf(contract)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{contract.title}.pdf"'
        return response

    @action(detail=True, methods=["get"], url_path="versions")
    def versions(self, request, pk=None):
        contract = self.get_object()
        return Response(ContractVersionSerializer(contract.versions.all(), many=True).data)
