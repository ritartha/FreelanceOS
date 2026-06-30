from django.urls import path

from apps.quotations.api.views import (
    PublicQuotationAcceptView,
    PublicQuotationDeclineView,
    PublicQuotationView,
)

app_name = "quotations-public"

urlpatterns = [
    path("public/quotations/<uuid:token>/", PublicQuotationView.as_view(), name="public-quotation"),
    path("public/quotations/<uuid:token>/accept/", PublicQuotationAcceptView.as_view(), name="public-quotation-accept"),
    path("public/quotations/<uuid:token>/decline/", PublicQuotationDeclineView.as_view(), name="public-quotation-decline"),
]
