from rest_framework.routers import DefaultRouter

from apps.tasks.api.views import TaskViewSet

app_name = "tasks"

router = DefaultRouter()
router.register("", TaskViewSet, basename="task")

urlpatterns = router.urls
