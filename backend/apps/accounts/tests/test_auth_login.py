import pytest
from django.core.management import call_command
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIClient

from apps.accounts.api.serializers import LoginSerializer
from apps.accounts.services import auth_service
from apps.common.exceptions import ValidationError


@pytest.mark.django_db
def test_login_serializer_invalid_credentials_returns_authentication_failed(monkeypatch):
    monkeypatch.setattr("apps.accounts.api.serializers.authenticate", lambda **kwargs: None)

    serializer = LoginSerializer(data={"email": "USER@example.com", "password": "bad-password"})

    with pytest.raises(AuthenticationFailed) as exc:
        serializer.is_valid(raise_exception=True)

    assert str(exc.value.detail) == "Invalid email or password."


@pytest.mark.django_db
def test_login_api_uses_issue_tokens_for_user(monkeypatch, django_user_model):
    user_kwargs = {
        "email": "user@example.com",
        "password": "P@ssword123",
        "first_name": "Test",
        "last_name": "User",
    }
    user = django_user_model.objects.create_user(**user_kwargs)

    monkeypatch.setattr(
        auth_service,
        "login_user",
        lambda *args, **kwargs: pytest.fail("LoginAPIView should not call login_user."),
    )
    monkeypatch.setattr(
        auth_service,
        "issue_tokens_for_user",
        lambda _user, request=None: {"user": _user, "access_token": "access", "refresh_token": "refresh"},
    )

    client = APIClient()
    response = client.post(
        "/api/v1/auth/login/",
        {"email": "USER@example.com", "password": "P@ssword123"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["access_token"] == "access"
    assert response.data["refresh_token"] == "refresh"
    assert response.data["user"]["email"] == "user@example.com"


@pytest.mark.django_db
def test_issue_tokens_for_user_rejects_inactive_user(django_user_model):
    user_kwargs = {
        "email": "inactive@example.com",
        "password": "P@ssword123",
        "first_name": "Inactive",
        "last_name": "User",
        "is_active": False,
    }
    user = django_user_model.objects.create_user(**user_kwargs)

    with pytest.raises(ValidationError) as exc:
        auth_service.issue_tokens_for_user(user)

    assert str(exc.value) == "This account has been deactivated."


@pytest.mark.django_db
def test_ensure_superuser_command_creates_superuser(monkeypatch, django_user_model):
    monkeypatch.setenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "StrongPass123")
    monkeypatch.setenv("DJANGO_SUPERUSER_FIRST_NAME", "Admin")
    monkeypatch.setenv("DJANGO_SUPERUSER_LAST_NAME", "User")

    call_command("ensure_superuser")

    admin = django_user_model.objects.get(email="admin@example.com")
    assert admin.is_superuser is True
    assert admin.is_staff is True
