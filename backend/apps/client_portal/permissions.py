"""
DRF permission class for Client Portal endpoints.

Portal views use `permission_classes = [IsPortalClient]` instead of
`IsAuthenticated`. This class:
  1. Decodes the JWT and checks for the portal_client_id claim.
  2. Loads the ClientPortalAccess + Client and attaches them to request
     as `request.portal_client` and `request.portal_tenant`.
  3. Returns 403 if the token is missing, invalid, or the access row
     is inactive.

Standard IsAuthenticated views are completely unaffected.
"""

import logging

from rest_framework.permissions import BasePermission

from apps.client_portal.services.auth_service import PORTAL_CLAIM

logger = logging.getLogger(__name__)


class IsPortalClient(BasePermission):
    message = "Valid client portal authentication required."

    def has_permission(self, request, view):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return False

        token_str = auth_header.split(" ", 1)[1]
        try:
            from rest_framework_simplejwt.tokens import AccessToken

            token = AccessToken(token_str)
            client_id = token.get(PORTAL_CLAIM)
            tenant_id = token.get("portal_tenant_id")
        except Exception:
            return False

        if not client_id or not tenant_id:
            return False

        try:
            from apps.client_portal.models import ClientPortalAccess

            access = ClientPortalAccess.objects.select_related("client", "tenant").get(
                client_id=client_id, tenant_id=tenant_id, is_active=True
            )
        except ClientPortalAccess.DoesNotExist:
            return False

        # Attach to request so portal views can use them without re-querying
        request.portal_client = access.client
        request.portal_tenant = access.tenant
        return True
