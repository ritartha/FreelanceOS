from rest_framework.routers import DefaultRouter

from apps.invoices.api.views import InvoiceLineItemViewSet, InvoiceViewSet

app_name = "invoices"

router = DefaultRouter()
router.register("", InvoiceViewSet, basename="invoice")
router.register("line-items", InvoiceLineItemViewSet, basename="invoice-line-item")

urlpatterns = router.urls
