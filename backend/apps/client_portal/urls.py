from django.http import HttpResponse
from django.urls import path

app_name = "client-portal"

urlpatterns = [
    path("", lambda request: HttpResponse("Client Portal"), name="index"),
]
