from rest_framework.routers import DefaultRouter

from apps.time_tracking.api.views import TimeLogViewSet

app_name = "time-logs"

router = DefaultRouter()
router.register("", TimeLogViewSet, basename="time-log")

urlpatterns = router.urls
