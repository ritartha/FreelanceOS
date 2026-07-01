"""
CSV export helpers for reports.
Returns a string of CSV content ready to be sent as an HTTP response.
"""

import csv
import io
from datetime import date


def _writer(rows: list[dict], fieldnames: list[str]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def export_revenue_csv(tenant, start_date: date = None, end_date: date = None) -> str:
    from apps.reports.services.report_service import get_monthly_revenue
    rows = get_monthly_revenue(tenant, start_date, end_date)
    return _writer(rows, ["month", "total"])


def export_expenses_csv(tenant, start_date: date = None, end_date: date = None) -> str:
    from apps.reports.services.report_service import get_monthly_expenses
    rows = get_monthly_expenses(tenant, start_date, end_date)
    return _writer(rows, ["month", "total"])


def export_top_clients_csv(tenant, start_date: date = None, end_date: date = None) -> str:
    from apps.reports.services.report_service import get_top_clients
    rows = get_top_clients(tenant, start_date, end_date)
    return _writer(rows, ["client_name", "total_invoiced", "invoice_count"])


def export_monthly_trends_csv(tenant, start_date: date = None, end_date: date = None) -> str:
    from apps.reports.services.report_service import get_monthly_trends
    rows = get_monthly_trends(tenant, start_date, end_date)
    return _writer(rows, ["month", "revenue", "expenses", "profit"])


def export_invoices_csv(tenant, start_date: date = None, end_date: date = None) -> str:
    from apps.invoices.models import Invoice
    qs = Invoice.objects.filter(tenant=tenant, is_deleted=False).select_related("client")
    if start_date:
        qs = qs.filter(issue_date__gte=start_date)
    if end_date:
        qs = qs.filter(issue_date__lte=end_date)

    rows = [
        {
            "invoice_number": inv.invoice_number,
            "client": inv.client.name,
            "issue_date": inv.issue_date,
            "due_date": inv.due_date,
            "total": inv.total,
            "amount_paid": inv.amount_paid,
            "amount_due": inv.amount_due,
            "status": inv.status,
        }
        for inv in qs
    ]
    return _writer(rows, ["invoice_number", "client", "issue_date", "due_date", "total", "amount_paid", "amount_due", "status"])


def export_expenses_detail_csv(tenant, start_date: date = None, end_date: date = None) -> str:
    from apps.expenses.models import Expense
    qs = Expense.objects.filter(tenant=tenant, is_deleted=False)
    if start_date:
        qs = qs.filter(expense_date__gte=start_date)
    if end_date:
        qs = qs.filter(expense_date__lte=end_date)

    rows = [
        {
            "date": exp.expense_date,
            "category": exp.category,
            "description": exp.description,
            "amount": exp.amount,
        }
        for exp in qs
    ]
    return _writer(rows, ["date", "category", "description", "amount"])
