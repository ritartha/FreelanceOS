from django.http import HttpResponse
from django.urls import path

app_name = "expenses"

urlpatterns = [
    path("", lambda request: HttpResponse("Expenses"), name="index"),
]
