from rest_framework.routers import DefaultRouter

from apps.projects.api.views import ProjectViewSet

app_name = "projects"

router = DefaultRouter()
router.register("", ProjectViewSet, basename="project")

urlpatterns = router.urls
