"""
Standardized API response helpers for FreelanceOS.

All API responses should use these helpers to produce a consistent
JSON envelope format.
"""

from rest_framework import status
from rest_framework.response import Response


def success_response(data=None, message=None, status_code=status.HTTP_200_OK, **kwargs):
    """
    Produce a standardized success response.

    {
        "success": true,
        "message": "...",
        "data": { ... }
    }
    """
    payload = {"success": True}
    if message:
        payload["message"] = message
    if data is not None:
        payload["data"] = data
    payload.update(kwargs)
    return Response(payload, status=status_code)


def created_response(data=None, message="Created successfully."):
    """Response for 201 Created."""
    return success_response(data=data, message=message, status_code=status.HTTP_201_CREATED)


def no_content_response():
    """Response for 204 No Content (e.g. deletes)."""
    return Response(status=status.HTTP_204_NO_CONTENT)


def error_response(message, code="error", details=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Produce a standardized error response.

    {
        "success": false,
        "error": {
            "code": "error_code",
            "message": "Human-readable message",
            "details": { ... }
        }
    }
    """
    return Response(
        {
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            },
        },
        status=status_code,
    )


def validation_error_response(errors, message="Validation failed."):
    """Response for validation errors (400)."""
    return error_response(
        message=message,
        code="validation_error",
        details=errors,
        status_code=status.HTTP_400_BAD_REQUEST,
    )


def not_found_response(message="The requested resource was not found."):
    """Response for 404 Not Found."""
    return error_response(
        message=message,
        code="not_found",
        status_code=status.HTTP_404_NOT_FOUND,
    )


def forbidden_response(message="You do not have permission to perform this action."):
    """Response for 403 Forbidden."""
    return error_response(
        message=message,
        code="permission_denied",
        status_code=status.HTTP_403_FORBIDDEN,
    )
