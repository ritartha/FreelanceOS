"""
API v1 URL Configuration for FreelanceOS.

All API endpoints are namespaced under /api/v1/.
"""

from django.urls import include, path

app_name = "api-v1"

urlpatterns = [
    path("auth/", include("apps.accounts.api.urls", namespace="auth")),
    path("dashboard/", include("apps.dashboard.api.urls", namespace="dashboard")),
    path("tenants/", include("apps.tenants.api.urls", namespace="tenants-api")),
    path("audit/", include("apps.audit.api.urls", namespace="audit-api")),
    path("", include("apps.crm.api.urls", namespace="crm")),
    path("projects/", include("apps.projects.api.urls", namespace="projects")),
    path("tasks/", include("apps.tasks.api.urls", namespace="tasks")),
    path("time-logs/", include("apps.time_tracking.api.urls", namespace="time-logs")),
    path("invoices/", include("apps.invoices.api.urls", namespace="invoices")),
    path("expenses/", include("apps.expenses.api.urls", namespace="expenses")),
    path("reports/", include("apps.reports.api.urls", namespace="reports")),
    path("files/", include("apps.files.api.urls", namespace="files")),
    path("notifications/", include("apps.notifications.api.urls", namespace="notifications")),
]
