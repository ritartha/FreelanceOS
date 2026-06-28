from django.http import HttpResponse
from django.urls import path

app_name = "files"

urlpatterns = [
    path("", lambda request: HttpResponse("Files"), name="index"),
]
