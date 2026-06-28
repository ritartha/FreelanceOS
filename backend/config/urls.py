"""
URL Configuration for FreelanceOS.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    """Simple health check endpoint for load balancers and monitoring."""
    return JsonResponse({"status": "ok", "service": "freelanceos"})


urlpatterns = [
    # Health check
    path("health/", health_check, name="health-check"),

    # Admin
    path("admin/", admin.site.urls),

    # API v1
    path("api/v1/", include("config.api_urls", namespace="api-v1")),

    # Server-rendered views
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("dashboard/", include("apps.dashboard.urls", namespace="dashboard")),
    path("crm/", include("apps.crm.urls", namespace="crm")),
    path("projects/", include("apps.projects.urls", namespace="projects")),
    path("tasks/", include("apps.tasks.urls", namespace="tasks")),
    path("time-tracking/", include("apps.time_tracking.urls", namespace="time-tracking")),
    path("invoices/", include("apps.invoices.urls", namespace="invoices")),
    path("expenses/", include("apps.expenses.urls", namespace="expenses")),
    path("reports/", include("apps.reports.urls", namespace="reports")),
    path("files/", include("apps.files.urls", namespace="files")),
    path("notifications/", include("apps.notifications.urls", namespace="notifications")),

    # Root redirect to dashboard
    path("", lambda request: __import__("django.shortcuts", fromlist=["redirect"]).redirect("/dashboard/")),
]

# Debug toolbar
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    try:
        import debug_toolbar
        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

# Admin site customization
admin.site.site_header = "FreelanceOS Administration"
admin.site.site_title = "FreelanceOS Admin"
admin.site.index_title = "Platform Administration"
