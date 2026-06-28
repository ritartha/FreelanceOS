"""
Common validators for FreelanceOS.

Reusable field validators used across serializers and models.
"""

import re

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import URLValidator
from django.utils.deconstruct import deconstructible


@deconstructible
class PhoneNumberValidator:
    """
    Validates phone numbers in E.164 or common formats.
    Allows digits, spaces, hyphens, parentheses, and leading +.
    """

    message = "Enter a valid phone number (e.g., +1-234-567-8900)."
    code = "invalid_phone"

    PHONE_REGEX = re.compile(r"^\+?[\d\s\-\(\)]{7,20}$")

    def __call__(self, value):
        if not self.PHONE_REGEX.match(value):
            raise DjangoValidationError(self.message, code=self.code)


@deconstructible
class CurrencyCodeValidator:
    """Validates ISO 4217 currency codes (3 uppercase letters)."""

    message = "Enter a valid ISO 4217 currency code (e.g., USD, EUR, INR)."
    code = "invalid_currency"

    CURRENCY_REGEX = re.compile(r"^[A-Z]{3}$")

    def __call__(self, value):
        if not self.CURRENCY_REGEX.match(value):
            raise DjangoValidationError(self.message, code=self.code)


@deconstructible
class FileSizeValidator:
    """
    Validates that a file does not exceed the maximum size.

    Args:
        max_size_mb: Maximum file size in megabytes (default: 10MB).
    """

    code = "file_too_large"

    def __init__(self, max_size_mb=10):
        self.max_size_mb = max_size_mb
        self.message = f"File size must not exceed {max_size_mb}MB."

    def __call__(self, value):
        if value.size > self.max_size_mb * 1024 * 1024:
            raise DjangoValidationError(self.message, code=self.code)


@deconstructible
class FileTypeValidator:
    """
    Validates that a file has an allowed extension.

    Args:
        allowed_extensions: List of allowed extensions (e.g., ['.pdf', '.jpg']).
    """

    code = "invalid_file_type"

    def __init__(self, allowed_extensions=None):
        self.allowed_extensions = allowed_extensions or [
            ".pdf", ".doc", ".docx", ".xls", ".xlsx",
            ".jpg", ".jpeg", ".png", ".gif", ".svg",
            ".zip", ".rar", ".csv", ".txt",
        ]
        ext_list = ", ".join(self.allowed_extensions)
        self.message = f"File type not allowed. Allowed types: {ext_list}"

    def __call__(self, value):
        import os

        ext = os.path.splitext(value.name)[1].lower()
        if ext not in self.allowed_extensions:
            raise DjangoValidationError(self.message, code=self.code)


# Singleton instances for common use
validate_phone = PhoneNumberValidator()
validate_currency = CurrencyCodeValidator()
validate_file_size_10mb = FileSizeValidator(max_size_mb=10)
validate_file_size_25mb = FileSizeValidator(max_size_mb=25)
validate_common_file_types = FileTypeValidator()
validate_image_types = FileTypeValidator(allowed_extensions=[".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"])
