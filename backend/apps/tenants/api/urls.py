from rest_framework.routers import DefaultRouter

from apps.tenants.api.views import MembershipViewSet, RoleViewSet, TenantViewSet

app_name = "tenants-api"

router = DefaultRouter()
router.register("tenants", TenantViewSet, basename="tenant")
router.register("roles", RoleViewSet, basename="role")
router.register("memberships", MembershipViewSet, basename="membership")

urlpatterns = router.urls
