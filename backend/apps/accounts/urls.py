from django.contrib.auth.views import LogoutView
from django.http import HttpResponse
from django.urls import path

app_name = "accounts"


def _placeholder(page_name):
    def view(request):
        return HttpResponse(f"{page_name} page")

    return view


urlpatterns = [
    path("login/", _placeholder("login"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", _placeholder("register"), name="register"),
    path("verify-email/", _placeholder("verify-email"), name="verify-email"),
    path("password-reset/", _placeholder("password-reset"), name="password-reset"),
    path("password-reset/confirm/", _placeholder("password-reset-confirm"), name="password-reset-confirm"),
]
