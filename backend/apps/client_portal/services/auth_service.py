"""
Client Portal auth service.

Uses Django's built-in password hashers (same as User passwords) and
issues a JWT with a custom claim so portal views can identify the client
without going through the standard User/Membership resolution path.
"""

import logging

from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import EmailMessage
from django.utils import timezone

logger = logging.getLogger(__name__)

# JWT claim key that identifies a portal session
PORTAL_CLAIM = "portal_client_id"


def _issue_portal_jwt(portal_access) -> dict:
    """
    Issue a JWT pair with a custom portal_client_id claim.
    Uses simplejwt's internals so the token format stays consistent.
    """
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken()
    refresh[PORTAL_CLAIM] = str(portal_access.client_id)
    refresh["portal_tenant_id"] = str(portal_access.tenant_id)
    refresh["email"] = portal_access.email

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "client_id": str(portal_access.client_id),
    }


def portal_login(email: str, password: str, tenant) -> dict:
    """
    Authenticate a client against their portal password.
    Returns a JWT pair dict on success, raises ValueError on failure.
    """
    from apps.client_portal.models import ClientPortalAccess

    try:
        access = ClientPortalAccess.objects.get(
            email=email, tenant=tenant, is_active=True
        )
    except ClientPortalAccess.DoesNotExist:
        raise ValueError("Invalid credentials.")

    if not access.password_hash:
        raise ValueError("Portal password not set. Use the invite link to set up your account.")

    if not check_password(password, access.password_hash):
        raise ValueError("Invalid credentials.")

    access.last_login_at = timezone.now()
    access.save(update_fields=["last_login_at"])

    return _issue_portal_jwt(access)


def set_portal_password(invite_token: str, new_password: str) -> dict:
    """
    Called when a client clicks their invite link and sets a password.
    Returns a JWT pair so the client is immediately logged in.
    """
    from apps.client_portal.models import ClientPortalAccess

    try:
        access = ClientPortalAccess.objects.get(invite_token=invite_token, is_active=True)
    except ClientPortalAccess.DoesNotExist:
        raise ValueError("Invalid or expired invite token.")

    if access.invite_accepted_at:
        raise ValueError("This invite link has already been used.")

    access.password_hash = make_password(new_password)
    access.invite_accepted_at = timezone.now()
    access.last_login_at = timezone.now()
    access.save(update_fields=["password_hash", "invite_accepted_at", "last_login_at"])

    return _issue_portal_jwt(access)


def send_portal_invite(portal_access, base_url: str = "") -> None:
    """
    Send the invite email to the client with a link to set their password.
    base_url should be the frontend URL, e.g. 'https://app.freelanceos.io'
    """
    invite_url = f"{base_url}/portal/setup/{portal_access.invite_token}/"
    EmailMessage(
        subject="You've been invited to the Client Portal",
        body=(
            f"Hi {portal_access.client.name},\n\n"
            f"You've been given access to the FreelanceOS Client Portal.\n\n"
            f"Click the link below to set up your password and log in:\n"
            f"{invite_url}\n\n"
            f"This link is valid for 7 days."
        ),
        to=[portal_access.email],
    ).send(fail_silently=False)

    portal_access.invite_sent_at = timezone.now()
    portal_access.save(update_fields=["invite_sent_at"])
