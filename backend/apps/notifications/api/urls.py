from rest_framework.routers import DefaultRouter

from apps.notifications.api.views import NotificationViewSet

app_name = "notifications"

router = DefaultRouter()
router.register("", NotificationViewSet, basename="notification")

urlpatterns = router.urls
