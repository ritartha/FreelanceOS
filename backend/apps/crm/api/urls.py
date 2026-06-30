from rest_framework.routers import DefaultRouter

from apps.crm.api.views import (
    ClientViewSet,
    CommunicationHistoryViewSet,
    CompanyViewSet,
    ContactViewSet,
    TagViewSet,
)

app_name = "crm"

router = DefaultRouter()
router.register("clients", ClientViewSet, basename="client")
router.register("contacts", ContactViewSet, basename="contact")
router.register("companies", CompanyViewSet, basename="company")
router.register("tags", TagViewSet, basename="tag")
router.register("communications", CommunicationHistoryViewSet, basename="communication")

urlpatterns = router.urls
