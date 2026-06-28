"""
Base repository class for FreelanceOS.

Provides a consistent data access pattern for tenant-scoped models.
All domain-specific repositories should inherit from BaseRepository.
"""

import logging

from django.db.models import Q

from apps.common.exceptions import NotFoundError

logger = logging.getLogger(__name__)


class BaseRepository:
    """
    Base repository providing common CRUD operations for TenantAwareModel subclasses.

    Usage:
        class ClientRepository(BaseRepository):
            model = Client
    """

    model = None  # Override in subclass

    def __init__(self, tenant=None):
        self.tenant = tenant

    def _base_queryset(self):
        """Return the base queryset, filtered by tenant if set."""
        qs = self.model.objects.all()
        if self.tenant:
            qs = qs.filter(tenant=self.tenant)
        return qs

    def get_by_id(self, pk):
        """Get a single record by primary key."""
        try:
            return self._base_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            raise NotFoundError(
                message=f"{self.model.__name__} with id '{pk}' not found."
            )

    def get_by_id_or_none(self, pk):
        """Get a single record by primary key, or None if not found."""
        try:
            return self._base_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            return None

    def list(self, ordering=None, **filters):
        """
        List records with optional filters and ordering.

        Args:
            ordering: Tuple of field names to order by (e.g. ('-created_at',)).
            **filters: Keyword arguments passed to .filter().
        """
        qs = self._base_queryset().filter(**filters)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def search(self, query, search_fields):
        """
        Full-text search across multiple fields.

        Args:
            query: Search string.
            search_fields: List of field names to search (supports __icontains).
        """
        if not query or not search_fields:
            return self._base_queryset()

        q = Q()
        for field in search_fields:
            q |= Q(**{f"{field}__icontains": query})
        return self._base_queryset().filter(q)

    def create(self, **kwargs):
        """Create and return a new record."""
        if self.tenant and "tenant" not in kwargs:
            kwargs["tenant"] = self.tenant
        return self.model.objects.create(**kwargs)

    def update(self, pk, **kwargs):
        """Update a record by primary key and return it."""
        instance = self.get_by_id(pk)
        for field, value in kwargs.items():
            setattr(instance, field, value)
        instance.save(update_fields=list(kwargs.keys()) + ["updated_at"])
        return instance

    def soft_delete(self, pk, user=None):
        """Soft-delete a record by primary key."""
        instance = self.get_by_id(pk)
        instance.soft_delete(user=user)
        return instance

    def hard_delete(self, pk):
        """Permanently delete a record by primary key."""
        instance = self.get_by_id(pk)
        instance.delete()

    def exists(self, **filters):
        """Check if any records matching the filters exist."""
        return self._base_queryset().filter(**filters).exists()

    def count(self, **filters):
        """Count records matching the filters."""
        return self._base_queryset().filter(**filters).count()

    def bulk_create(self, instances):
        """Bulk-create records."""
        if self.tenant:
            for instance in instances:
                if not hasattr(instance, "tenant_id") or not instance.tenant_id:
                    instance.tenant = self.tenant
        return self.model.objects.bulk_create(instances)

    def filter(self, **kwargs):
        """Filter records with keyword arguments."""
        return self._base_queryset().filter(**kwargs)
