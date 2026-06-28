from django.http import HttpResponse
from django.urls import path

app_name = "invoices"

urlpatterns = [
    path("", lambda request: HttpResponse("Invoices"), name="index"),
]
