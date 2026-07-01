from django.http import HttpResponse
from django.urls import path

app_name = "contracts"

urlpatterns = [
    path("", lambda request: HttpResponse("Contracts"), name="index"),
]
