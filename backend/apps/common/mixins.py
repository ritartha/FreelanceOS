"""
Common view mixins for FreelanceOS.

Reusable mixins for DRF views and Django CBVs.
"""

from django.contrib.auth.mixins import LoginRequiredMixin

from apps.common.exceptions import TenantRequiredError


class TenantQuerysetMixin:
    """
    DRF ViewSet mixin that auto-filters querysets by the current tenant.

    Requires TenantContextMiddleware to have set request.tenant.
    Also auto-sets tenant and created_by/updated_by on create/update.
    """

    def _resolve_tenant(self):
        if getattr(self.request, "tenant", None):
            return self.request.tenant
            
        # In DRF, request.user might be resolved after middleware runs (e.g. JWT)
        if self.request.user and self.request.user.is_authenticated:
            from apps.tenants.models import Membership
            membership = Membership.objects.filter(
                user=self.request.user, 
                status="active", 
                tenant__is_active=True
            ).order_by("-created_at").first()
            
            if membership:
                self.request.membership = membership
                self.request.tenant = membership.tenant
                return membership.tenant
                
        return None

    def get_queryset(self):
        """Filter queryset by the current tenant."""
        qs = super().get_queryset()
        tenant = self._resolve_tenant()
        if tenant:
            return qs.filter(tenant=tenant)
            
        raise TenantRequiredError()

    def perform_create(self, serializer):
        """Auto-set tenant and created_by on create."""
        tenant = self._resolve_tenant()
        if not tenant:
            raise TenantRequiredError()
            
        serializer.save(
            tenant=tenant,
            created_by=self.request.user,
        )

    def perform_update(self, serializer):
        """Auto-set updated_by on update."""
        serializer.save(
            updated_by=self.request.user,
        )


class AuditMixin:
    """
    Mixin that logs create/update/delete actions to the audit trail.

    Override get_audit_action() to customize the action name.
    """

    def perform_create(self, serializer):
        instance = serializer.save(
            tenant=getattr(self.request, "tenant", None),
            created_by=self.request.user,
        )
        self._log_audit("create", instance)
        return instance

    def perform_update(self, serializer):
        instance = serializer.save(
            updated_by=self.request.user,
        )
        self._log_audit("update", instance)
        return instance

    def perform_destroy(self, instance):
        self._log_audit("delete", instance)
        instance.soft_delete(user=self.request.user)

    def _log_audit(self, action, instance):
        """Log the action to audit trail. Fails silently if audit app unavailable."""
        try:
            from apps.audit.services.audit_service import log_action

            log_action(
                tenant=self.request.tenant,
                user=self.request.user,
                action=action,
                entity_type=instance.__class__.__name__,
                entity_id=str(instance.pk),
                request=self.request,
            )
        except Exception:
            pass  # Audit logging should never break business logic


class TenantViewMixin(LoginRequiredMixin):
    """
    Django CBV mixin for tenant-scoped template views.

    Ensures user is authenticated and has a tenant context.
    Filters querysets by tenant automatically.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, "tenant") and self.request.tenant:
            return qs.filter(tenant=self.request.tenant)
        return qs.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tenant"] = getattr(self.request, "tenant", None)
        return context
