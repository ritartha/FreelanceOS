from rest_framework.routers import DefaultRouter

from apps.files.api.views import FileAttachmentViewSet

app_name = "files"

router = DefaultRouter()
router.register("", FileAttachmentViewSet, basename="file-attachment")

urlpatterns = router.urls
