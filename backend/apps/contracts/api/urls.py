from rest_framework.routers import DefaultRouter

from apps.contracts.api.views import ContractViewSet

app_name = "contracts"

router = DefaultRouter()
router.register("", ContractViewSet, basename="contract")

urlpatterns = router.urls
