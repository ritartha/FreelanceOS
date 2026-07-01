import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def refresh_dashboard_cache(tenant_id: str):
    """
    Recomputes all dashboard KPIs for a single tenant and stores in Redis cache.
    Triggered on-demand from the dashboard view on cache miss.
    """
    from django.core.cache import cache
    data = _compute_dashboard_data(tenant_id)
    cache.set(f"dashboard:{tenant_id}", data, timeout=900)
    logger.info("Dashboard cache refreshed for tenant %s", tenant_id)
    return tenant_id


def _compute_dashboard_data(tenant_id: str) -> dict:
    import calendar as _cal
    from datetime import date
    from decimal import Decimal

    from django.db.models import Sum
    from django.utils import timezone

    try:
        from apps.tenants.models import Tenant
        tenant = Tenant.objects.get(id=tenant_id)
    except Exception:
        logger.warning("_compute_dashboard_data: tenant %s not found", tenant_id)
        return {}

    from apps.contracts.models import Contract
    from apps.crm.models import Client
    from apps.expenses.models import Expense
    from apps.invoices.models import Invoice
    from apps.projects.models import Project
    from apps.tasks.models import Task

    today          = timezone.now().date()
    first_of_month = today.replace(day=1)

    if today.month == 1:
        last_month_start = date(today.year - 1, 12, 1)
        last_month_end   = date(today.year - 1, 12, 31)
    else:
        last_month_start = date(today.year, today.month - 1, 1)
        last_month_end   = date(
            today.year, today.month - 1,
            _cal.monthrange(today.year, today.month - 1)[1],
        )

    projects_active  = Project.objects.filter(tenant=tenant, status="active",    is_deleted=False).count()
    tasks_open       = Task.objects.filter(tenant=tenant, is_deleted=False).exclude(status__in=["done", "cancelled"]).count()
    invoices_pending = Invoice.objects.filter(tenant=tenant, is_deleted=False).exclude(status__in=["paid", "cancelled"]).count()
    expenses_count   = Expense.objects.filter(tenant=tenant, is_deleted=False).count()

    rev_this = Invoice.objects.filter(
        tenant=tenant, status=Invoice.StatusChoices.PAID,
        paid_at__date__gte=first_of_month, paid_at__date__lte=today, is_deleted=False,
    ).aggregate(t=Sum("total"))["t"] or Decimal("0")

    rev_last = Invoice.objects.filter(
        tenant=tenant, status=Invoice.StatusChoices.PAID,
        paid_at__date__gte=last_month_start, paid_at__date__lte=last_month_end, is_deleted=False,
    ).aggregate(t=Sum("total"))["t"] or Decimal("0")

    delta_pct = float((rev_this - rev_last) / rev_last * 100) if rev_last > 0 else 0.0

    outstanding = Invoice.objects.filter(
        tenant=tenant, is_deleted=False,
    ).exclude(status__in=["paid", "cancelled"]).aggregate(t=Sum("amount_due"))["t"] or Decimal("0")

    overdue_count = Invoice.objects.filter(
        tenant=tenant, status=Invoice.StatusChoices.OVERDUE, is_deleted=False,
    ).count()

    in_7_days = today + timezone.timedelta(days=7)
    upcoming  = []
    for task in Task.objects.filter(
        tenant=tenant, due_date__gte=today, due_date__lte=in_7_days, is_deleted=False,
    ).exclude(status__in=["done", "cancelled"]).order_by("due_date")[:5]:
        upcoming.append({"type": "task", "title": task.title, "due": str(task.due_date), "id": str(task.id)})

    for project in Project.objects.filter(
        tenant=tenant, due_date__gte=today, due_date__lte=in_7_days, is_deleted=False,
    ).exclude(status__in=["completed", "cancelled"]).order_by("due_date")[:5]:
        upcoming.append({"type": "project", "title": project.name, "due": str(project.due_date), "id": str(project.id)})

    upcoming.sort(key=lambda x: x["due"])

    recent_clients = list(
        Client.objects.filter(tenant=tenant, is_deleted=False)
        .order_by("-created_at")[:5]
        .values("id", "name", "created_at")
    )
    for c in recent_clients:
        c["id"] = str(c["id"])
        c["created_at"] = str(c["created_at"])

    contracts_expiring = Contract.objects.filter(
        tenant=tenant, is_deleted=False,
        status__in=[Contract.StatusChoices.ACTIVE, Contract.StatusChoices.SIGNED],
        end_date__gte=today,
        end_date__lte=today + timezone.timedelta(days=30),
    ).count()

    return {
        "projects":                projects_active,
        "tasks":                   tasks_open,
        "invoices":                invoices_pending,
        "expenses":                expenses_count,
        "revenue_this_month":      str(rev_this),
        "revenue_last_month":      str(rev_last),
        "revenue_delta_pct":       round(delta_pct, 2),
        "outstanding_amount":      str(outstanding),
        "overdue_invoices":        overdue_count,
        "upcoming_deadlines":      upcoming[:10],
        "recent_clients":          recent_clients,
        "contracts_expiring_soon": contracts_expiring,
    }
