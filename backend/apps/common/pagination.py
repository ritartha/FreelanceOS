"""
DRF Pagination classes for FreelanceOS.
"""

from rest_framework.pagination import CursorPagination, PageNumberPagination


class StandardPageNumberPagination(PageNumberPagination):
    """
    Standard page-number pagination with configurable page size.

    Query params:
    - page: Page number (default: 1)
    - page_size: Number of results per page (default: 25, max: 100)
    """

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "count": {"type": "integer"},
                "next": {"type": "string", "nullable": True},
                "previous": {"type": "string", "nullable": True},
                "results": schema,
            },
        }


class StandardCursorPagination(CursorPagination):
    """
    Cursor-based pagination for consistent ordering on large datasets.

    Query params:
    - cursor: Opaque cursor string
    - page_size: Number of results per page (default: 25, max: 100)
    """

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100
    ordering = "-created_at"
