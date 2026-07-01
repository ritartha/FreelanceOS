from rest_framework.routers import DefaultRouter

from apps.invoices.api.views import InvoiceViewSet, RecurringInvoiceViewSet

app_name = "invoices"

router = DefaultRouter()
router.register("recurring", RecurringInvoiceViewSet, basename="recurring-invoice")
router.register("", InvoiceViewSet, basename="invoice")

urlpatterns = router.urls
