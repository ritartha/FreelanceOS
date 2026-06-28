from django.http import HttpResponse
from django.urls import path

app_name = "tasks"

urlpatterns = [
    path("", lambda request: HttpResponse("Tasks"), name="index"),
]
