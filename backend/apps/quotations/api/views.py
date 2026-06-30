from django.http import HttpResponse
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.mixins import TenantQuerysetMixin
from apps.quotations.api.serializers import (
    PublicQuotationSerializer,
    QuotationSerializer,
    QuotationVersionSerializer,
)
from apps.quotations.models import Quotation
from apps.quotations.services.email_service import accept_quotation, decline_quotation
from apps.quotations.services.pdf_service import render_quotation_pdf
from apps.quotations.services.quotation_service import (
    recalculate_line_item_total,
    recalculate_totals,
    snapshot_version,
)


class QuotationViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Quotation.objects.all()
    serializer_class = QuotationSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        client_id = self.request.query_params.get("client")
        if client_id:
            qs = qs.filter(client_id=client_id)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def perform_create(self, serializer):
        tenant = self._resolve_tenant()
        quotation = serializer.save(
            tenant=tenant,
            created_by=self.request.user,
            quotation_number=Quotation.generate_quotation_number(tenant),
        )
        for line_item in quotation.line_items.all():
            recalculate_line_item_total(line_item)
        recalculate_totals(quotation)

    def perform_update(self, serializer):
        instance = self.get_object()
        # Sent (or further along) quotations get a version snapshot before
        # any edit, so the history of what the client was actually shown
        # is preserved — draft quotations don't need this overhead.
        if instance.status != Quotation.StatusChoices.DRAFT:
            snapshot_version(instance, user=self.request.user)

        quotation = serializer.save(updated_by=self.request.user)
        for line_item in quotation.line_items.all():
            recalculate_line_item_total(line_item)
        recalculate_totals(quotation)

    @action(detail=True, methods=["post"], url_path="send")
    def send(self, request, pk=None):
        from apps.quotations.tasks import send_quotation_email_task

        quotation = self.get_object()
        recipient = request.data.get("recipient_email")
        send_quotation_email_task.delay(str(quotation.id), recipient)
        return Response({"detail": "Quotation email queued."})

    @action(detail=True, methods=["get"], url_path="pdf")
    def pdf(self, request, pk=None):
        quotation = self.get_object()
        pdf_bytes = render_quotation_pdf(quotation)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{quotation.quotation_number}.pdf"'
        return response

    @action(detail=True, methods=["get"], url_path="versions")
    def versions(self, request, pk=None):
        quotation = self.get_object()
        return Response(QuotationVersionSerializer(quotation.versions.all(), many=True).data)


class PublicQuotationView(APIView):
    """
    Unauthenticated endpoints backing the shareable quotation link:
        GET  /api/v1/public/quotations/<token>/
        POST /api/v1/public/quotations/<token>/accept/
        POST /api/v1/public/quotations/<token>/decline/
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, token):
        from django.shortcuts import get_object_or_404

        quotation = get_object_or_404(Quotation, public_token=token)
        if quotation.status == Quotation.StatusChoices.SENT:
            quotation.status = Quotation.StatusChoices.VIEWED
            quotation.save(update_fields=["status", "updated_at"])
        return Response(PublicQuotationSerializer(quotation).data)


class PublicQuotationAcceptView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, token):
        from django.shortcuts import get_object_or_404

        quotation = get_object_or_404(Quotation, public_token=token)
        quotation = accept_quotation(quotation)
        return Response(PublicQuotationSerializer(quotation).data)


class PublicQuotationDeclineView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, token):
        from django.shortcuts import get_object_or_404

        quotation = get_object_or_404(Quotation, public_token=token)
        quotation = decline_quotation(quotation)
        return Response(PublicQuotationSerializer(quotation).data)
