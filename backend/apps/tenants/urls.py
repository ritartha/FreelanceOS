from django.http import HttpResponse
from django.urls import path

app_name = "tenants"

urlpatterns = [
    path("", lambda request: HttpResponse("Tenants"), name="index"),
]
