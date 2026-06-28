from django.http import HttpResponse
from django.urls import path

app_name = "audit"

urlpatterns = [
    path("", lambda request: HttpResponse("Audit"), name="index"),
]
