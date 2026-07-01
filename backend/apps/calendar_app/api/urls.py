from rest_framework.routers import DefaultRouter

from apps.calendar_app.api.views import CalendarEventViewSet

app_name = "calendar"

router = DefaultRouter()
router.register("events", CalendarEventViewSet, basename="calendar-event")

urlpatterns = router.urls
