from django.http import HttpResponse
from django.urls import path

app_name = "crm"

urlpatterns = [
    path("", lambda request: HttpResponse("CRM"), name="index"),
]
