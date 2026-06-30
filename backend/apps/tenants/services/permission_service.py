"""
Permission-checking service for FreelanceOS.

Role.permissions is a JSON field shaped like:
    {"projects": ["view", "edit"], "invoices": ["view"], "*": ["*"]}

"*" as a module key or action means full access. Owners/Admins implicitly
have everything regardless of the JSON contents.
"""

from apps.tenants.models import Membership


def has_permission(membership: Membership, module: str, action: str) -> bool:
    """
    Check whether a Membership's Role grants `action` on `module`.

    Owner/Admin roles always pass. Otherwise looks up Role.permissions JSON.
    """
    if membership is None:
        return False

    if membership.role.name in ("Owner", "Admin"):
        return True

    perms = membership.role.permissions or {}

    if "*" in perms and ("*" in perms["*"] or action in perms["*"]):
        return True

    module_perms = perms.get(module, [])
    return "*" in module_perms or action in module_perms


def get_membership_for_request(request):
    """Resolve the active Membership for the current request/tenant, or None."""
    if not hasattr(request, "tenant") or request.tenant is None:
        return None
    if not request.user or not request.user.is_authenticated:
        return None
    return Membership.objects.filter(
        tenant=request.tenant,
        user=request.user,
        status=Membership.StatusChoices.ACTIVE,
    ).select_related("role").first()
