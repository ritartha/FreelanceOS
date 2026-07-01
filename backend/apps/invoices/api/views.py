from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.mixins import TenantQuerysetMixin
from apps.invoices.api.serializers import (
    InvoiceSerializer,
    PaymentSerializer,
    RecurringInvoiceSerializer,
)
from apps.invoices.models import Invoice, Payment, RecurringInvoice
from apps.invoices.services.invoice_service import (
    convert_quotation_to_invoice,
    import_time_logs_to_invoice,
    recalculate_line_item_total,
    recalculate_totals,
    record_payment,
)
from apps.invoices.services.pdf_service import render_invoice_pdf


class InvoiceViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

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
        return qs

    def perform_create(self, serializer):
        tenant = self._resolve_tenant()
        invoice = serializer.save(
            tenant=tenant,
            created_by=self.request.user,
            invoice_number=Invoice.generate_invoice_number(tenant),
        )
        for li in invoice.line_items.all():
            recalculate_line_item_total(li)
        recalculate_totals(invoice)

    def perform_update(self, serializer):
        invoice = serializer.save(updated_by=self.request.user)
        for li in invoice.line_items.all():
            recalculate_line_item_total(li)
        recalculate_totals(invoice)

    @action(detail=True, methods=["post"], url_path="record-payment")
    def record_payment_action(self, request, pk=None):
        invoice = self.get_object()
        amount = request.data.get("amount")
        method = request.data.get("method", Payment.MethodChoices.BANK_TRANSFER)
        paid_on = request.data.get("paid_on")
        reference = request.data.get("reference", "")
        notes = request.data.get("notes", "")

        if not amount or not paid_on:
            return Response({"detail": "amount and paid_on are required."}, status=400)

        from decimal import Decimal
        payment = record_payment(
            invoice, Decimal(str(amount)), method, paid_on,
            reference=reference, notes=notes, user=request.user,
        )
        return Response(PaymentSerializer(payment).data, status=201)

    @action(detail=True, methods=["get"], url_path="pdf")
    def pdf(self, request, pk=None):
        invoice = self.get_object()
        pdf_bytes = render_invoice_pdf(invoice)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{invoice.invoice_number}.pdf"'
        return response

    @action(detail=True, methods=["post"], url_path="import-time-logs")
    def import_time_logs(self, request, pk=None):
        invoice = self.get_object()
        time_log_ids = request.data.get("time_log_ids", [])
        if not time_log_ids:
            return Response({"detail": "time_log_ids list is required."}, status=400)
        count = import_time_logs_to_invoice(invoice, time_log_ids, user=request.user)
        return Response({"detail": f"{count} line item(s) created from time logs."})

    @action(detail=False, methods=["post"], url_path="from-quotation")
    def from_quotation(self, request):
        quotation_id = request.data.get("quotation_id")
        if not quotation_id:
            return Response({"detail": "quotation_id is required."}, status=400)
        from apps.quotations.models import Quotation
        try:
            quotation = Quotation.objects.get(id=quotation_id, tenant=self._resolve_tenant())
        except Quotation.DoesNotExist:
            return Response({"detail": "Quotation not found."}, status=404)
        invoice = convert_quotation_to_invoice(quotation, user=request.user)
        return Response(InvoiceSerializer(invoice).data, status=201)


class RecurringInvoiceViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = RecurringInvoice.objects.all()
    serializer_class = RecurringInvoiceSerializer

    def perform_create(self, serializer):
        tenant = self._resolve_tenant()
        serializer.save(tenant=tenant, created_by=self.request.user)
