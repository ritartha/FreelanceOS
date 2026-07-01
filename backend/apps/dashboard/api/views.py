import logging

from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.dashboard.tasks import _compute_dashboard_data, refresh_dashboard_cache

logger = logging.getLogger(__name__)

_EMPTY = {
    "projects": 0,
    "tasks": 0,
    "invoices": 0,
    "expenses": 0,
    "revenue_this_month": "0",
    "revenue_last_month": "0",
    "revenue_delta_pct": 0.0,
    "outstanding_amount": "0",
    "overdue_invoices": 0,
    "upcoming_deadlines": [],
    "recent_clients": [],
    "contracts_expiring_soon": 0,
}


class DashboardSummaryAPIView(APIView):
    def get(self, request):
        tenant = getattr(request, "tenant", None)

        if not tenant and request.user and request.user.is_authenticated:
            from apps.tenants.models import Membership
            membership = Membership.objects.filter(
                user=request.user,
                status="active",
                tenant__is_active=True,
            ).order_by("-created_at").first()
            if membership:
                tenant = membership.tenant

        if not tenant:
            return Response(_EMPTY)

        cache_key = f"dashboard:{tenant.id}"
        data = cache.get(cache_key)

        if data is None:
            logger.debug("Dashboard cache miss for tenant %s — computing live", tenant.id)
            data = _compute_dashboard_data(str(tenant.id))
            cache.set(cache_key, data, timeout=900)
            # Trigger async refresh so the next request benefits from a pre-warmed cache
            try:
                refresh_dashboard_cache.delay(str(tenant.id))
            except Exception:
                pass  # Celery may not be running in dev

        return Response(data)
