"""
Reports aggregation service.

All functions take a tenant + optional date range (start_date, end_date)
and return plain dicts/lists ready to be serialized directly.
No models needed — reports read from existing app models.
"""

from datetime import date
from decimal import Decimal

from django.db.models import Count, DecimalField, ExpressionWrapper, F, FloatField, Q, Sum
from django.db.models.functions import TruncMonth


# ── Revenue ────────────────────────────────────────────────────────────────────

def get_revenue_summary(tenant, start_date: date = None, end_date: date = None) -> dict:
    """Total revenue from paid/partial invoices within the date range."""
    from apps.invoices.models import Invoice, Payment

    payment_qs = Payment.objects.filter(
        tenant=tenant, is_deleted=False
    )
    if start_date:
        payment_qs = payment_qs.filter(paid_on__gte=start_date)
    if end_date:
        payment_qs = payment_qs.filter(paid_on__lte=end_date)

    total_received = payment_qs.aggregate(total=Sum("amount"))["total"] or Decimal("0")

    invoice_qs = Invoice.objects.filter(tenant=tenant, is_deleted=False)
    if start_date:
        invoice_qs = invoice_qs.filter(issue_date__gte=start_date)
    if end_date:
        invoice_qs = invoice_qs.filter(issue_date__lte=end_date)

    total_invoiced = invoice_qs.exclude(
        status="cancelled"
    ).aggregate(total=Sum("total"))["total"] or Decimal("0")

    total_outstanding = invoice_qs.filter(
        status__in=["sent", "viewed", "partial", "overdue"]
    ).aggregate(total=Sum("amount_due"))["total"] or Decimal("0")

    return {
        "total_invoiced": total_invoiced,
        "total_received": total_received,
        "total_outstanding": total_outstanding,
    }


def get_monthly_revenue(tenant, start_date: date = None, end_date: date = None) -> list:
    """Revenue per month from payments."""
    from apps.invoices.models import Payment

    qs = Payment.objects.filter(tenant=tenant, is_deleted=False)
    if start_date:
        qs = qs.filter(paid_on__gte=start_date)
    if end_date:
        qs = qs.filter(paid_on__lte=end_date)

    rows = (
        qs.annotate(month=TruncMonth("paid_on"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )
    return [
        {"month": r["month"].strftime("%Y-%m"), "total": r["total"]}
        for r in rows
    ]


# ── Expenses ───────────────────────────────────────────────────────────────────

def get_expense_summary(tenant, start_date: date = None, end_date: date = None) -> dict:
    """Total expenses and breakdown by category."""
    from apps.expenses.models import Expense

    qs = Expense.objects.filter(tenant=tenant, is_deleted=False)
    if start_date:
        qs = qs.filter(expense_date__gte=start_date)
    if end_date:
        qs = qs.filter(expense_date__lte=end_date)

    total = qs.aggregate(total=Sum("amount"))["total"] or Decimal("0")
    by_category = list(
        qs.values("category")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )
    return {"total_expenses": total, "by_category": by_category}


def get_monthly_expenses(tenant, start_date: date = None, end_date: date = None) -> list:
    from apps.expenses.models import Expense

    qs = Expense.objects.filter(tenant=tenant, is_deleted=False)
    if start_date:
        qs = qs.filter(expense_date__gte=start_date)
    if end_date:
        qs = qs.filter(expense_date__lte=end_date)

    rows = (
        qs.annotate(month=TruncMonth("expense_date"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )
    return [
        {"month": r["month"].strftime("%Y-%m"), "total": r["total"]}
        for r in rows
    ]


# ── Profit ─────────────────────────────────────────────────────────────────────

def get_profit_summary(tenant, start_date: date = None, end_date: date = None) -> dict:
    revenue = get_revenue_summary(tenant, start_date, end_date)
    expenses = get_expense_summary(tenant, start_date, end_date)
    received = revenue["total_received"]
    total_expenses = expenses["total_expenses"]
    profit = received - total_expenses
    margin = (
        round((profit / received) * 100, 2) if received > 0 else Decimal("0")
    )
    return {
        "revenue": received,
        "expenses": total_expenses,
        "profit": profit,
        "margin_percent": margin,
    }


# ── Tax ────────────────────────────────────────────────────────────────────────

def get_tax_summary(tenant, start_date: date = None, end_date: date = None) -> dict:
    """Total tax collected across paid invoices."""
    from apps.invoices.models import Invoice

    qs = Invoice.objects.filter(
        tenant=tenant,
        is_deleted=False,
        status__in=["paid", "partial"],
    )
    if start_date:
        qs = qs.filter(issue_date__gte=start_date)
    if end_date:
        qs = qs.filter(issue_date__lte=end_date)

    total_tax = qs.aggregate(total=Sum("tax_amount"))["total"] or Decimal("0")
    return {"total_tax_collected": total_tax}


# ── Top clients ────────────────────────────────────────────────────────────────

def get_top_clients(tenant, start_date: date = None, end_date: date = None, limit: int = 10) -> list:
    """Clients ranked by total invoiced amount."""
    from apps.invoices.models import Invoice

    qs = Invoice.objects.filter(
        tenant=tenant, is_deleted=False
    ).exclude(status="cancelled")
    if start_date:
        qs = qs.filter(issue_date__gte=start_date)
    if end_date:
        qs = qs.filter(issue_date__lte=end_date)

    rows = (
        qs.values("client__id", "client__name")
        .annotate(total_invoiced=Sum("total"), invoice_count=Count("id"))
        .order_by("-total_invoiced")[:limit]
    )
    return [
        {
            "client_id": str(r["client__id"]),
            "client_name": r["client__name"],
            "total_invoiced": r["total_invoiced"],
            "invoice_count": r["invoice_count"],
        }
        for r in rows
    ]


# ── Monthly trends (combined revenue + expenses) ──────────────────────────────

def get_monthly_trends(tenant, start_date: date = None, end_date: date = None) -> list:
    """
    Combined month-by-month revenue and expense data for charting.
    Returns a list of {month, revenue, expenses, profit} dicts.
    """
    revenue_by_month = {
        r["month"]: r["total"] for r in get_monthly_revenue(tenant, start_date, end_date)
    }
    expense_by_month = {
        r["month"]: r["total"] for r in get_monthly_expenses(tenant, start_date, end_date)
    }

    all_months = sorted(set(list(revenue_by_month.keys()) + list(expense_by_month.keys())))

    return [
        {
            "month": m,
            "revenue": revenue_by_month.get(m, Decimal("0")),
            "expenses": expense_by_month.get(m, Decimal("0")),
            "profit": revenue_by_month.get(m, Decimal("0")) - expense_by_month.get(m, Decimal("0")),
        }
        for m in all_months
    ]
