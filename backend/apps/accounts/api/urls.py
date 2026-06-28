from django.urls import path

from apps.accounts.api.views import (
    AuthTokenRefreshAPIView,
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    PasswordChangeAPIView,
    PasswordResetAPIView,
    PasswordResetRequestAPIView,
    RegisterAPIView,
    VerifyEmailAPIView,
)

app_name = "auth"

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("token/refresh/", AuthTokenRefreshAPIView.as_view(), name="token-refresh"),
    path("verify-email/", VerifyEmailAPIView.as_view(), name="verify-email"),
    path("password/reset-request/", PasswordResetRequestAPIView.as_view(), name="password-reset-request"),
    path("password/reset/", PasswordResetAPIView.as_view(), name="password-reset"),
    path("password/change/", PasswordChangeAPIView.as_view(), name="password-change"),
    path("me/", MeAPIView.as_view(), name="me"),
]
