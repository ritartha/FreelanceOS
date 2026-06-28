"""
Utility functions for FreelanceOS.

UUID generation, slug helpers, date helpers, file path generators.
"""

import os
import uuid
from datetime import date, datetime, timedelta

from django.utils import timezone
from django.utils.text import slugify as django_slugify


# =============================================================================
# UUID Helpers
# =============================================================================


def generate_uuid():
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


def generate_short_uuid(length=8):
    """Generate a short UUID string (first N characters of a UUID4 hex)."""
    return uuid.uuid4().hex[:length]


# =============================================================================
# Slug Helpers
# =============================================================================


def unique_slugify(text, max_length=50):
    """
    Generate a URL-safe slug from text, appending a short UUID for uniqueness.
    """
    base_slug = django_slugify(text)[:max_length - 9]  # Leave room for -XXXXXXXX
    return f"{base_slug}-{generate_short_uuid()}"


# =============================================================================
# Date / Time Helpers
# =============================================================================


def now():
    """Return the current timezone-aware datetime."""
    return timezone.now()


def today():
    """Return the current date."""
    return date.today()


def days_from_now(days):
    """Return a date N days from today."""
    return today() + timedelta(days=days)


def start_of_month(dt=None):
    """Return the first day of the given month."""
    dt = dt or today()
    return dt.replace(day=1)


def end_of_month(dt=None):
    """Return the last day of the given month."""
    dt = dt or today()
    if dt.month == 12:
        return dt.replace(day=31)
    return dt.replace(month=dt.month + 1, day=1) - timedelta(days=1)


def start_of_year(dt=None):
    """Return Jan 1 of the given year."""
    dt = dt or today()
    return dt.replace(month=1, day=1)


def date_range(start, end):
    """Yield each date in [start, end] inclusive."""
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def format_duration(total_seconds):
    """Format a duration in seconds to a human-readable string (e.g. '2h 15m')."""
    if total_seconds is None or total_seconds < 0:
        return "0m"
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    if hours > 0 and minutes > 0:
        return f"{hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{minutes}m"


# =============================================================================
# File Path Generators
# =============================================================================


def tenant_upload_path(instance, filename):
    """
    Generate an upload path scoped to the tenant.
    Result: uploads/<tenant_id>/<model_name>/<uuid>.<ext>
    """
    ext = os.path.splitext(filename)[1].lower()
    model_name = instance.__class__.__name__.lower()
    tenant_id = getattr(instance, "tenant_id", "shared")
    return f"uploads/{tenant_id}/{model_name}/{uuid.uuid4().hex}{ext}"


def avatar_upload_path(instance, filename):
    """Generate upload path for user avatars."""
    ext = os.path.splitext(filename)[1].lower()
    return f"avatars/{instance.id}{ext}"


def receipt_upload_path(instance, filename):
    """Generate upload path for expense receipts."""
    ext = os.path.splitext(filename)[1].lower()
    tenant_id = getattr(instance, "tenant_id", "shared")
    return f"uploads/{tenant_id}/receipts/{uuid.uuid4().hex}{ext}"


# =============================================================================
# Formatting Helpers
# =============================================================================


def format_currency(amount, currency="USD"):
    """Format a decimal amount with currency symbol."""
    symbols = {
        "USD": "$", "EUR": "€", "GBP": "£", "INR": "₹",
        "JPY": "¥", "CNY": "¥", "CAD": "C$", "AUD": "A$",
    }
    symbol = symbols.get(currency, currency + " ")
    if amount is None:
        return f"{symbol}0.00"
    return f"{symbol}{amount:,.2f}"


def truncate_string(text, max_length=100, suffix="..."):
    """Truncate a string to max_length, appending suffix if truncated."""
    if not text or len(text) <= max_length:
        return text or ""
    return text[:max_length - len(suffix)] + suffix
