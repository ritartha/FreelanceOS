from django.urls import path

from apps.proposals.api.views import (
    PublicProposalAcceptView,
    PublicProposalDeclineView,
    PublicProposalView,
)

app_name = "proposals-public"

urlpatterns = [
    path("public/proposals/<uuid:token>/", PublicProposalView.as_view(), name="public-proposal"),
    path("public/proposals/<uuid:token>/accept/", PublicProposalAcceptView.as_view(), name="public-proposal-accept"),
    path("public/proposals/<uuid:token>/decline/", PublicProposalDeclineView.as_view(), name="public-proposal-decline"),
]
