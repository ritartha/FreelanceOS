from rest_framework.routers import DefaultRouter

from apps.audit.api.views import AuditLogViewSet

app_name = "audit-api"

router = DefaultRouter()
router.register("logs", AuditLogViewSet, basename="audit-log")

urlpatterns = router.urls
