def _client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class AuditContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.audit_context = {
            "ip_address": _client_ip(request),
            "user_agent": request.META.get("HTTP_USER_AGENT", "")[:500],
            "method": request.method,
            "path": request.path,
        }
        return self.get_response(request)
