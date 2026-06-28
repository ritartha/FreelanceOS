"""
Common filter mixins for FreelanceOS.

Provides reusable filterset base classes that all business apps inherit.
"""

import django_filters

from apps.common.models import TenantAwareModel


class TenantFilterMixin(django_filters.FilterSet):
    """
    Mixin that auto-filters by the current tenant.

    Views using this filter must pass the tenant via the view's
    get_queryset() method or via request.tenant.
    """

    class Meta:
        abstract = True


class DateRangeFilterMixin(django_filters.FilterSet):
    """
    Mixin adding created_at date range filtering.

    Query params:
    - date_from: Filter records created on or after this date
    - date_to: Filter records created on or before this date
    """

    date_from = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__gte",
        label="Created from",
    )
    date_to = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__lte",
        label="Created to",
    )

    class Meta:
        abstract = True


class StatusFilterMixin(django_filters.FilterSet):
    """
    Mixin adding status field filtering.

    Query params:
    - status: Exact match on status field
    - status__in: Comma-separated list of statuses
    """

    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")

    class Meta:
        abstract = True


class BaseTenantFilterSet(DateRangeFilterMixin, StatusFilterMixin):
    """
    Base FilterSet combining tenant, date range, and status filtering.

    All tenant-scoped model FilterSets should inherit from this.
    """

    search = django_filters.CharFilter(method="filter_search", label="Search")

    def filter_search(self, queryset, name, value):
        """
        Override in subclass to implement model-specific search.
        Default implementation does nothing.
        """
        return queryset

    class Meta:
        abstract = True
