from django.http import HttpResponse
from django.urls import path

app_name = "notifications"

urlpatterns = [
    path("", lambda request: HttpResponse("Notifications"), name="index"),
]
