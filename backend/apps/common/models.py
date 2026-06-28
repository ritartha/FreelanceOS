"""
Common abstract models for FreelanceOS.

All tenant-scoped business models should inherit from TenantAwareModel
to get automatic tenant filtering, soft delete, and audit timestamps.
"""

import uuid

from django.conf import settings
from django.db import models


# =============================================================================
# Managers
# =============================================================================


class SoftDeleteManager(models.Manager):
    """Default manager that filters out soft-deleted records."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    """Manager that includes soft-deleted records."""

    pass


class TenantAwareManager(SoftDeleteManager):
    """
    Manager that filters by tenant and excludes soft-deleted records.
    Usage: MyModel.objects.for_tenant(tenant)
    """

    def for_tenant(self, tenant):
        """Filter queryset by tenant."""
        return self.get_queryset().filter(tenant=tenant)

    def for_tenant_id(self, tenant_id):
        """Filter queryset by tenant ID."""
        return self.get_queryset().filter(tenant_id=tenant_id)


# =============================================================================
# Abstract Models
# =============================================================================


class TimeStampedModel(models.Model):
    """
    Abstract model with created_at and updated_at timestamps.

    Use this for non-tenant models (e.g. system-level models).
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class TenantAwareModel(TimeStampedModel):
    """
    Abstract model for all tenant-scoped business entities.

    Provides:
    - UUID primary key
    - Tenant FK (set automatically via middleware)
    - Created/updated by user tracking
    - Soft delete with is_deleted flag and deleted_at timestamp
    - JSONB metadata field for extensibility
    - Default manager that auto-filters deleted records and tenant scope
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
        db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
    )

    # Soft delete
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_deleted",
    )

    # Extensibility
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Arbitrary key-value metadata for extensibility.",
    )

    # Managers
    objects = TenantAwareManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def soft_delete(self, user=None):
        """Mark the record as deleted without removing from the database."""
        from django.utils import timezone

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by", "updated_at"])

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by", "updated_at"])
