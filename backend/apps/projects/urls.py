from django.http import HttpResponse
from django.urls import path

app_name = "projects"

urlpatterns = [
    path("", lambda request: HttpResponse("Projects"), name="index"),
]
