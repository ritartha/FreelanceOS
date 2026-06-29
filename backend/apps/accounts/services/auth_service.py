"""
Authentication service for FreelanceOS.

Business logic for user registration, login, email verification,
password reset, and session management.
"""

import logging
import re

from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import SessionLog, User
from apps.accounts.services.token_service import (
    consume_password_reset_token,
    consume_verification_token,
    generate_password_reset_token,
    generate_verification_token,
)
from apps.common.exceptions import ConflictError, NotFoundError, ValidationError

logger = logging.getLogger(__name__)


@transaction.atomic
def register_user(email, password, first_name, last_name, **extra_fields):
    """
    Register a new user account.

    Creates the user with is_email_verified=False, generates an email
    verification token, and bootstraps a personal Tenant + Owner Membership
    so that TenantContextMiddleware always resolves a tenant after sign-up.

    Returns:
        tuple: (user, verification_token)
    """
    email = email.lower().strip()

    if User.objects.filter(email=email).exists():
        raise ConflictError(message="An account with this email already exists.")

    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        **extra_fields,
    )

    # --- Bootstrap personal workspace ---
    from apps.tenants.models import Membership, Role, Tenant

    # Build a URL-safe slug from the local part of the email, deduplicated
    slug_base = re.sub(r"[^a-z0-9]+", "-", email.split("@")[0].lower()).strip("-")
    slug = slug_base
    counter = 1
    while Tenant.objects.filter(slug=slug).exists():
        slug = f"{slug_base}-{counter}"
        counter += 1

    tenant = Tenant.objects.create(
        name=f"{first_name}'s Workspace",
        slug=slug,
        owner=user,
    )

    # Each tenant gets its own "Owner" role
    owner_role = Role.objects.create(
        tenant=tenant,
        name="Owner",
        permissions={},
    )

    Membership.objects.create(
        user=user,
        tenant=tenant,
        role=owner_role,
        status=Membership.StatusChoices.ACTIVE,
        joined_at=timezone.now(),
    )
    # --- End bootstrap ---

    verification_token = generate_verification_token(user)

    logger.info(f"User registered: {user.email}")
    return user, verification_token


def login_user(email, password, request=None):
    """
    Authenticate a user and issue JWT tokens.

    Returns:
        dict: {user, access_token, refresh_token}

    Raises:
        ValidationError: If credentials are invalid.
    """
    email = email.lower().strip()
    user = authenticate(email=email, password=password)

    if user is None:
        raise ValidationError(message="Invalid email or password.")

    return issue_tokens_for_user(user, request=request)


def issue_tokens_for_user(user, request=None):
    """Issue JWT tokens for an already-authenticated user."""
    if not user.is_active:
        raise ValidationError(message="This account has been deactivated.")

    # Update last login
    user.last_login_at = timezone.now()
    user.save(update_fields=["last_login_at"])

    # Create session log
    if request:
        _create_session_log(user, request)

    # Issue JWT tokens
    refresh = RefreshToken.for_user(user)

    logger.info(f"User logged in: {user.email}")
    return {
        "user": user,
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
    }


def verify_email(token_string):
    """
    Verify a user's email address using a verification token.

    Returns the user.
    """
    user = consume_verification_token(token_string)
    logger.info(f"Email verified: {user.email}")
    return user


def request_password_reset(email):
    """
    Initiate a password reset by generating a reset token.

    Returns the token string, or None if the user doesn't exist
    (to prevent user enumeration).
    """
    email = email.lower().strip()

    try:
        user = User.objects.get(email=email, is_active=True)
    except User.DoesNotExist:
        # Don't reveal whether the email exists
        logger.info(f"Password reset requested for non-existent email: {email}")
        return None

    token = generate_password_reset_token(user)
    logger.info(f"Password reset token generated for {user.email}")
    return token


def reset_password(token_string, new_password):
    """
    Reset a user's password using a reset token.

    Returns the user.
    """
    user = consume_password_reset_token(token_string, new_password)
    logger.info(f"Password reset completed for {user.email}")
    return user


def change_password(user, old_password, new_password):
    """
    Change a user's password (requires old password verification).
    """
    if not user.check_password(old_password):
        raise ValidationError(message="Current password is incorrect.")

    user.set_password(new_password)
    user.save(update_fields=["password"])
    logger.info(f"Password changed for {user.email}")


def update_profile(user, **fields):
    """
    Update a user's profile fields.

    Allowed fields: first_name, last_name, phone, timezone, avatar.
    """
    allowed_fields = {"first_name", "last_name", "phone", "timezone", "avatar"}
    update_fields = []

    for field, value in fields.items():
        if field in allowed_fields:
            setattr(user, field, value)
            update_fields.append(field)

    if update_fields:
        user.save(update_fields=update_fields)
        logger.info(f"Profile updated for {user.email}: {update_fields}")

    return user


def create_jwt_pair(user):
    """Issue a new JWT access/refresh pair for the user."""
    refresh = RefreshToken.for_user(user)
    return {
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
    }


def _create_session_log(user, request):
    """Create a session log entry."""
    ip = _get_client_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]
    SessionLog.objects.create(
        user=user,
        ip_address=ip,
        user_agent=user_agent,
    )


def _get_client_ip(request):
    """Extract client IP from request, handling proxies."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
