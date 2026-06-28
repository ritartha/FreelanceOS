from apps.tenants.models import Membership


class TenantContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant = None
        request.membership = None

        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            membership = (
                Membership.objects.select_related("tenant", "role")
                .filter(user=user, status=Membership.StatusChoices.ACTIVE, tenant__is_active=True)
                .order_by("-created_at")
                .first()
            )
            if membership:
                request.membership = membership
                request.tenant = membership.tenant

        return self.get_response(request)
