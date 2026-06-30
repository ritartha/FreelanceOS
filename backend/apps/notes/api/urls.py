from rest_framework.routers import DefaultRouter

from apps.notes.api.views import NoteAttachmentViewSet, NoteViewSet

app_name = "notes"

router = DefaultRouter()
router.register("notes", NoteViewSet, basename="note")
router.register("note-attachments", NoteAttachmentViewSet, basename="note-attachment")

urlpatterns = router.urls
