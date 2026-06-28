from django.http import HttpResponse
from django.urls import path

app_name = "dashboard"

urlpatterns = [
    path("", lambda request: HttpResponse("Dashboard"), name="home"),
]
