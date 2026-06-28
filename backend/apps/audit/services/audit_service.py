from apps.audit.models import AuditLog


def log_action(tenant, user, action, entity_type, entity_id, old_data=None, new_data=None, request=None):
    ip_address = None
    user_agent = ""

    if request is not None:
        audit_context = getattr(request, "audit_context", {})
        ip_address = audit_context.get("ip_address")
        user_agent = audit_context.get("user_agent", "")

    return AuditLog.objects.create(
        tenant=tenant,
        user=user,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        old_data=old_data,
        new_data=new_data,
        ip_address=ip_address,
        user_agent=user_agent,
    )
