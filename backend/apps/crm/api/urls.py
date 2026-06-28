from rest_framework.routers import DefaultRouter

from apps.crm.api.views import ClientViewSet, ContactViewSet

app_name = "crm"

router = DefaultRouter()
router.register("clients", ClientViewSet, basename="client")
router.register("contacts", ContactViewSet, basename="contact")

urlpatterns = router.urls
