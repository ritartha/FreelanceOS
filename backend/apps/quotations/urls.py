from django.http import HttpResponse
from django.urls import path

app_name = "quotations"

urlpatterns = [
    path("", lambda request: HttpResponse("Quotations"), name="index"),
]
