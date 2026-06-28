"""
Base service class for FreelanceOS.

All service classes should inherit from BaseService to get
tenant context injection, permission checking, and audit logging hooks.
"""

import logging

from apps.common.exceptions import (
    NotFoundError,
    PermissionDeniedError,
    TenantRequiredError,
)

logger = logging.getLogger(__name__)


class BaseService:
    """
    Base service class providing tenant context, permission checking,
    and audit logging hooks.

    Usage:
        class ClientService(BaseService):
            def create_client(self, data):
                self.require_permission('manage_crm')
                client = Client.objects.create(tenant=self.tenant, **data)
                self.log_audit('create', 'Client', client.id)
                return client
    """

    def __init__(self, tenant=None, user=None, request=None):
        """
        Initialize service with tenant and user context.

        Args:
            tenant: The Tenant instance for scoping operations.
            user: The User instance performing the action.
            request: The HTTP request (optional, for audit context).
        """
        self.tenant = tenant
        self.user = user
        self.request = request

    def require_tenant(self):
        """Raise TenantRequiredError if no tenant context is set."""
        if self.tenant is None:
            raise TenantRequiredError()

    def require_permission(self, permission_codename):
        """
        Check if the user has a specific permission within the tenant.

        Raises PermissionDeniedError if the check fails.
        """
        self.require_tenant()

        if self.user is None:
            raise PermissionDeniedError()

        # Superusers bypass permission checks
        if self.user.is_superuser:
            return

        # Tenant owner has all permissions
        if self.tenant.owner_id == self.user.id:
            return

        # Check membership role permissions
        try:
            from apps.tenants.models import Membership

            membership = Membership.objects.select_related("role").get(
                tenant=self.tenant,
                user=self.user,
                status="active",
            )
            permissions = membership.role.permissions or {}
            if not permissions.get(permission_codename, False):
                raise PermissionDeniedError(
                    message=f"You lack the '{permission_codename}' permission."
                )
        except Membership.DoesNotExist:
            raise PermissionDeniedError(
                message="You are not a member of this tenant."
            )

    def log_audit(self, action, entity_type, entity_id, old_data=None, new_data=None):
        """
        Log an action to the audit trail.
        Fails silently — audit logging must never break business logic.
        """
        try:
            from apps.audit.services.audit_service import log_action

            log_action(
                tenant=self.tenant,
                user=self.user,
                action=action,
                entity_type=entity_type,
                entity_id=str(entity_id),
                old_data=old_data,
                new_data=new_data,
                request=self.request,
            )
        except Exception as e:
            logger.warning(f"Failed to log audit event: {e}")

    def get_or_404(self, model_class, pk, tenant_scoped=True):
        """
        Get an object by PK, raising NotFoundError if not found.

        Args:
            model_class: The Django model class.
            pk: The primary key.
            tenant_scoped: If True, also filter by self.tenant.
        """
        filters = {"pk": pk}
        if tenant_scoped:
            self.require_tenant()
            filters["tenant"] = self.tenant

        try:
            return model_class.objects.get(**filters)
        except model_class.DoesNotExist:
            raise NotFoundError(
                message=f"{model_class.__name__} not found."
            )
