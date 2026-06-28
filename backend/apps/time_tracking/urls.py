from django.http import HttpResponse
from django.urls import path

app_name = "time-tracking"

urlpatterns = [
    path("", lambda request: HttpResponse("Time Tracking"), name="index"),
]
