from django.http import HttpResponse
from django.urls import path

app_name = "notes"

urlpatterns = [
    path("", lambda request: HttpResponse("Notes"), name="index"),
]
