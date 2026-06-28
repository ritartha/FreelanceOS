from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.dashboard.api.views import DashboardSummaryAPIView

app_name = "dashboard"

router = DefaultRouter()

urlpatterns = router.urls + [
    path("summary/", DashboardSummaryAPIView.as_view(), name="summary"),
]
