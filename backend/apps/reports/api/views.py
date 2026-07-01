import csv
from datetime import date

from django.http import HttpResponse
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.mixins import TenantQuerysetMixin
from apps.reports.services.csv_service import (
    export_expenses_csv,
    export_expenses_detail_csv,
    export_invoices_csv,
    export_monthly_trends_csv,
    export_revenue_csv,
    export_top_clients_csv,
)

from apps.reports.services.pdf_service import render_profit_report_pdf
from apps.reports.services.report_service import (
    get_expense_summary,
    get_monthly_expenses,
    get_monthly_revenue,
    get_monthly_trends,
    get_profit_summary,
    get_revenue_summary,
    get_tax_summary,
    get_top_clients,
)


def _parse_dates(request):
    """Parse optional start_date / end_date query params."""
    start = request.query_params.get("start_date")
    end = request.query_params.get("end_date")
    try:
        start = date.fromisoformat(start) if start else None
        end = date.fromisoformat(end) if end else None
    except ValueError:
        start = end = None
    return start, end


class ReportBaseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _tenant(self, request):
        from apps.common.mixins import TenantQuerysetMixin
        mixin = TenantQuerysetMixin()
        mixin.request = request
        return mixin._resolve_tenant()


class RevenueSummaryView(ReportBaseView):
    """GET /api/v1/reports/revenue/"""
    def get(self, request):
        start, end = _parse_dates(request)
        data = get_revenue_summary(self._tenant(request), start, end)
        return Response(data)


class MonthlyRevenueView(ReportBaseView):
    """GET /api/v1/reports/revenue/monthly/"""
    def get(self, request):
        start, end = _parse_dates(request)
        data = get_monthly_revenue(self._tenant(request), start, end)
        return Response(data)


class ExpenseSummaryView(ReportBaseView):
    """GET /api/v1/reports/expenses/"""
    def get(self, request):
        start, end = _parse_dates(request)
        data = get_expense_summary(self._tenant(request), start, end)
        return Response(data)


class MonthlyExpensesView(ReportBaseView):
    """GET /api/v1/reports/expenses/monthly/"""
    def get(self, request):
        start, end = _parse_dates(request)
        data = get_monthly_expenses(self._tenant(request), start, end)
        return Response(data)


class ProfitSummaryView(ReportBaseView):
    """GET /api/v1/reports/profit/"""
    def get(self, request):
        start, end = _parse_dates(request)
        data = get_profit_summary(self._tenant(request), start, end)
        return Response(data)


class TaxSummaryView(ReportBaseView):
    """GET /api/v1/reports/tax/"""
    def get(self, request):
        start, end = _parse_dates(request)
        data = get_tax_summary(self._tenant(request), start, end)
        return Response(data)


class TopClientsView(ReportBaseView):
    """GET /api/v1/reports/top-clients/?limit=10"""
    def get(self, request):
        start, end = _parse_dates(request)
        limit = int(request.query_params.get("limit", 10))
        data = get_top_clients(self._tenant(request), start, end, limit=limit)
        return Response(data)


class MonthlyTrendsView(ReportBaseView):
    """GET /api/v1/reports/trends/"""
    def get(self, request):
        start, end = _parse_dates(request)
        data = get_monthly_trends(self._tenant(request), start, end)
        return Response(data)


# ── CSV exports ────────────────────────────────────────────────────────────────

class ExportCSVView(ReportBaseView):
    """
    GET /api/v1/reports/export/csv/?type=<type>&start_date=&end_date=
    type: revenue | expenses | invoices | expenses_detail | trends | top_clients
    """
    EXPORT_MAP = {
        "revenue": (export_revenue_csv, "revenue"),
        "expenses": (export_expenses_csv, "expenses"),
        "invoices": (export_invoices_csv, "invoices"),
        "expenses_detail": (export_expenses_detail_csv, "expenses_detail"),
        "trends": (export_monthly_trends_csv, "trends"),
        "top_clients": (export_top_clients_csv, "top_clients"),
    }

    def get(self, request):
        export_type = request.query_params.get("type", "trends")
        if export_type not in self.EXPORT_MAP:
            return Response({"detail": f"Unknown export type. Choose from: {list(self.EXPORT_MAP.keys())}"}, status=400)

        start, end = _parse_dates(request)
        fn, label = self.EXPORT_MAP[export_type]
        csv_content = fn(self._tenant(request), start, end)

        response = HttpResponse(csv_content, content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{label}_report.csv"'
        return response


# ── PDF export ─────────────────────────────────────────────────────────────────

class ExportPDFView(ReportBaseView):
    """GET /api/v1/reports/export/pdf/?start_date=&end_date="""
    def get(self, request):
        start, end = _parse_dates(request)
        pdf_bytes = render_profit_report_pdf(self._tenant(request), start, end)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = 'inline; filename="profit_report.pdf"'
        return response
