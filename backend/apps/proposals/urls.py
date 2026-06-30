from django.http import HttpResponse
from django.urls import path

app_name = "proposals"

urlpatterns = [
    path("", lambda request: HttpResponse("Proposals"), name="index"),
]
