from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.client_portal.api.views import (
    ClientPortalAccessViewSet,
    PortalFileListView,
    PortalInvoiceListView,
    PortalLoginView,
    PortalMeView,
    PortalMessageListView,
    PortalMilestoneApproveView,
    PortalProjectListView,
    PortalQuotationAcceptView,
    PortalQuotationListView,
    PortalSetupView,
)

app_name = "client-portal"

router = DefaultRouter()
router.register("access", ClientPortalAccessViewSet, basename="portal-access")

urlpatterns = router.urls + [
    # Auth
    path("auth/login/", PortalLoginView.as_view(), name="portal-login"),
    path("auth/setup/", PortalSetupView.as_view(), name="portal-setup"),

    # Client-facing (portal JWT required)
    path("me/", PortalMeView.as_view(), name="portal-me"),
    path("projects/", PortalProjectListView.as_view(), name="portal-projects"),
    path("invoices/", PortalInvoiceListView.as_view(), name="portal-invoices"),
    path("quotations/", PortalQuotationListView.as_view(), name="portal-quotations"),
    path("quotations/<uuid:pk>/accept/", PortalQuotationAcceptView.as_view(), name="portal-quotation-accept"),
    path("files/", PortalFileListView.as_view(), name="portal-files"),
    path("messages/", PortalMessageListView.as_view(), name="portal-messages"),
    path("milestones/<uuid:pk>/approve/", PortalMilestoneApproveView.as_view(), name="portal-milestone-approve"),
]
