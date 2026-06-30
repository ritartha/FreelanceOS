from rest_framework.routers import DefaultRouter

from apps.files.api.views import FileAttachmentViewSet, FileTagViewSet, FolderViewSet

app_name = "files"

router = DefaultRouter()
router.register("folders", FolderViewSet, basename="folder")
router.register("file-tags", FileTagViewSet, basename="file-tag")
router.register("", FileAttachmentViewSet, basename="file-attachment")

urlpatterns = router.urls
