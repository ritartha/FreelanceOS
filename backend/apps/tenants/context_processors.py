def tenant_context(request):
    tenant = getattr(request, "tenant", None)
    if tenant is None:
        return {}
    return {"tenant": tenant}
