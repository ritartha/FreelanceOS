"""
DRF Permission classes for FreelanceOS.

These are used across the entire platform for tenant-based access control.
"""

from rest_framework.permissions import BasePermission


class TenantAccessPermission(BasePermission):
    """
    Ensures the user has access to the tenant in the request context.

    Requires that TenantContextMiddleware has set request.tenant.
    """

    message = "You do not have access to this tenant."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Tenant must be set by middleware
        return hasattr(request, "tenant") and request.tenant is not None

    def has_object_permission(self, request, view, obj):
        """Ensure the object belongs to the request's tenant."""
        if not hasattr(request, "tenant") or request.tenant is None:
            return False
        if hasattr(obj, "tenant_id"):
            return obj.tenant_id == request.tenant.id
        if hasattr(obj, "tenant"):
            return obj.tenant == request.tenant
        return True


class ObjectOwnerPermission(BasePermission):
    """
    Allows access only to the owner of the object.

    Checks obj.created_by == request.user.
    """

    message = "You can only modify objects you created."

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "created_by_id"):
            return obj.created_by_id == request.user.id
        if hasattr(obj, "created_by"):
            return obj.created_by == request.user
        return False


class IsEmailVerified(BasePermission):
    """
    Allows access only to users who have verified their email address.
    """

    message = "Please verify your email address to access this resource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, "is_email_verified", False)


class IsTenantOwner(BasePermission):
    """
    Allows access only to the owner of the current tenant.
    """

    message = "Only the tenant owner can perform this action."

    def has_permission(self, request, view):
        if not hasattr(request, "tenant") or request.tenant is None:
            return False
        return request.tenant.owner_id == request.user.id


class HasModulePermission(BasePermission):
    """
    Checks granular module/action permissions via Role.permissions JSON.

    Usage on a ViewSet:
        permission_classes = [HasModulePermission]
        permission_required = ("invoices", "edit")  # (module, action)

    Falls back to read-only ("view") for GET/HEAD/OPTIONS if permission_required
    is not set on the view.
    """

    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        from apps.tenants.services.permission_service import (
            get_membership_for_request,
            has_permission,
        )

        membership = get_membership_for_request(request)
        if membership is None:
            return False

        module, action = getattr(view, "permission_required", (None, None))
        if module is None:
            return True  # view didn't opt in; rely on other permission classes

        return has_permission(membership, module, action)
    """
    Allows access to tenant owners and members with admin role.
    """

    message = "Admin access required."

    def has_permission(self, request, view):
        if not hasattr(request, "tenant") or request.tenant is None:
            return False
        # Owner always has admin access
        if request.tenant.owner_id == request.user.id:
            return True
        # Check membership role
        return hasattr(request, "membership") and request.membership and (
            request.membership.role.name in ("Owner", "Admin")
        )
