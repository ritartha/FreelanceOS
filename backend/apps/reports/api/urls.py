from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.reports.api.views import ReportsStubAPIView

app_name = "reports"

router = DefaultRouter()

urlpatterns = router.urls + [
    path("", ReportsStubAPIView.as_view(), name="list"),
]
