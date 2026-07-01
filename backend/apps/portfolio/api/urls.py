from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.portfolio.api.views import PortfolioItemViewSet, PortfolioPublicDetailView

app_name = "portfolio"

router = DefaultRouter()
router.register("items", PortfolioItemViewSet, basename="portfolio-item")

urlpatterns = router.urls + [
    path("public/<slug:slug>/", PortfolioPublicDetailView.as_view(), name="public-portfolio-detail"),
]
