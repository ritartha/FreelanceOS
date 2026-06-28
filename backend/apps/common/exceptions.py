"""
Custom exception classes and DRF exception handler for FreelanceOS.

All service-layer exceptions inherit from ServiceException.
The custom_exception_handler produces a standardized JSON error envelope.
"""

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


# =============================================================================
# Service-Layer Exceptions
# =============================================================================


class ServiceException(Exception):
    """Base exception for service-layer errors."""

    default_message = "A service error occurred."
    default_code = "service_error"

    def __init__(self, message=None, code=None, details=None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(ServiceException):
    """Resource not found."""

    default_message = "The requested resource was not found."
    default_code = "not_found"


class PermissionDeniedError(ServiceException):
    """User lacks permission for this action."""

    default_message = "You do not have permission to perform this action."
    default_code = "permission_denied"


class ValidationError(ServiceException):
    """Validation error in service layer."""

    default_message = "The provided data is invalid."
    default_code = "validation_error"


class ConflictError(ServiceException):
    """Conflict with existing state (e.g. duplicate, concurrent edit)."""

    default_message = "The request conflicts with the current state."
    default_code = "conflict"


class RateLimitError(ServiceException):
    """Rate limit exceeded."""

    default_message = "Rate limit exceeded. Please try again later."
    default_code = "rate_limit_exceeded"


class TenantRequiredError(ServiceException):
    """Operation requires a tenant context."""

    default_message = "A tenant context is required for this operation."
    default_code = "tenant_required"


# =============================================================================
# DRF API Exceptions
# =============================================================================


class APINotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "The requested resource was not found."
    default_code = "not_found"


class APIConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "The request conflicts with the current state."
    default_code = "conflict"


# =============================================================================
# Custom DRF Exception Handler
# =============================================================================


def custom_exception_handler(exc, context):
    """
    Custom exception handler that produces a standardized JSON error envelope:

    {
        "success": false,
        "error": {
            "code": "error_code",
            "message": "Human-readable message",
            "details": { ... }
        }
    }
    """

    # Handle service-layer exceptions first
    if isinstance(exc, ServiceException):
        status_map = {
            NotFoundError: status.HTTP_404_NOT_FOUND,
            PermissionDeniedError: status.HTTP_403_FORBIDDEN,
            ValidationError: status.HTTP_400_BAD_REQUEST,
            ConflictError: status.HTTP_409_CONFLICT,
            RateLimitError: status.HTTP_429_TOO_MANY_REQUESTS,
            TenantRequiredError: status.HTTP_403_FORBIDDEN,
        }
        http_status = status_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

        from rest_framework.response import Response

        return Response(
            {
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                },
            },
            status=http_status,
        )

    # Let DRF handle its own exceptions
    response = exception_handler(exc, context)

    if response is not None:
        # Normalize DRF errors into our standard envelope
        error_data = response.data
        if isinstance(error_data, dict):
            message = error_data.get("detail", str(error_data))
            code = getattr(exc, "default_code", "error")
        elif isinstance(error_data, list):
            message = error_data[0] if error_data else "An error occurred."
            code = "error"
        else:
            message = str(error_data)
            code = "error"

        response.data = {
            "success": False,
            "error": {
                "code": code,
                "message": str(message),
                "details": error_data if isinstance(error_data, dict) else {},
            },
        }

    return response
