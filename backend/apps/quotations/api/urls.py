from rest_framework.routers import DefaultRouter

from apps.quotations.api.views import QuotationViewSet

app_name = "quotations"

router = DefaultRouter()
router.register("", QuotationViewSet, basename="quotation")

urlpatterns = router.urls
