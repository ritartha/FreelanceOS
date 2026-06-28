"""
Token service for email verification and password reset.

Generates, stores, and validates short-lived tokens.
"""

import logging
import secrets
from datetime import timedelta

from django.utils import timezone

from apps.accounts.models import EmailVerificationToken, PasswordResetToken

logger = logging.getLogger(__name__)


def generate_verification_token(user, hours_valid=24):
    """
    Generate an email verification token for the user.

    Invalidates any existing unused tokens.
    Returns the token string.
    """
    # Invalidate existing tokens
    EmailVerificationToken.objects.filter(
        user=user,
        used_at__isnull=True,
    ).update(used_at=timezone.now())

    token_string = secrets.token_urlsafe(32)
    EmailVerificationToken.objects.create(
        user=user,
        token=token_string,
        expires_at=timezone.now() + timedelta(hours=hours_valid),
    )
    logger.info(f"Generated email verification token for {user.email}")
    return token_string


def validate_verification_token(token_string):
    """
    Validate an email verification token.

    Returns the user if valid, raises ValueError otherwise.
    """
    try:
        token = EmailVerificationToken.objects.select_related("user").get(
            token=token_string,
        )
    except EmailVerificationToken.DoesNotExist:
        raise ValueError("Invalid verification token.")

    if not token.is_valid:
        if token.is_expired:
            raise ValueError("This verification link has expired.")
        if token.is_used:
            raise ValueError("This verification link has already been used.")
        raise ValueError("Invalid verification token.")

    return token


def consume_verification_token(token_string):
    """
    Validate and consume an email verification token.

    Marks the user's email as verified and the token as used.
    Returns the user.
    """
    token = validate_verification_token(token_string)
    user = token.user

    # Mark token as used
    token.used_at = timezone.now()
    token.save(update_fields=["used_at"])

    # Mark user email as verified
    user.is_email_verified = True
    user.save(update_fields=["is_email_verified"])

    logger.info(f"Email verified for {user.email}")
    return user


def generate_password_reset_token(user, hours_valid=1):
    """
    Generate a password reset token for the user.

    Invalidates any existing unused tokens.
    Returns the token string.
    """
    # Invalidate existing tokens
    PasswordResetToken.objects.filter(
        user=user,
        used_at__isnull=True,
    ).update(used_at=timezone.now())

    token_string = secrets.token_urlsafe(32)
    PasswordResetToken.objects.create(
        user=user,
        token=token_string,
        expires_at=timezone.now() + timedelta(hours=hours_valid),
    )
    logger.info(f"Generated password reset token for {user.email}")
    return token_string


def validate_password_reset_token(token_string):
    """
    Validate a password reset token.

    Returns the token if valid, raises ValueError otherwise.
    """
    try:
        token = PasswordResetToken.objects.select_related("user").get(
            token=token_string,
        )
    except PasswordResetToken.DoesNotExist:
        raise ValueError("Invalid reset token.")

    if not token.is_valid:
        if token.is_expired:
            raise ValueError("This reset link has expired.")
        raise ValueError("Invalid reset token.")

    return token


def consume_password_reset_token(token_string, new_password):
    """
    Validate and consume a password reset token.

    Sets the new password and marks the token as used.
    Returns the user.
    """
    token = validate_password_reset_token(token_string)
    user = token.user

    # Mark token as used
    token.used_at = timezone.now()
    token.save(update_fields=["used_at"])

    # Set new password
    user.set_password(new_password)
    user.save(update_fields=["password"])

    logger.info(f"Password reset completed for {user.email}")
    return user
