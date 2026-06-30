import logging
import re

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.tasks import send_verification_email_task
from apps.accounts.services.token_service import generate_verification_token

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def send_verification_email_on_user_create(sender, instance, created, **kwargs):
    if created and not instance.is_email_verified:
        token = generate_verification_token(instance)
        send_verification_email_task.delay(str(instance.id), token)


@receiver(post_save, sender=User)
def ensure_user_has_workspace(sender, instance, created, **kwargs):
    """
    Auto-bootstrap a personal workspace for newly created users who
    don't already have one (e.g. users created via createsuperuser or admin).
    The register_user() service also creates a workspace, but within a
    transaction — this signal acts as a safety net for other creation paths.
    """
    if not created:
        return

    from apps.tenants.models import Membership, Role, Tenant

    # Skip if user already has a membership (e.g. register_user() already ran)
    if Membership.objects.filter(user=instance).exists():
        return

    # Build a safe slug
    slug_base = re.sub(r"[^a-z0-9]+", "-", instance.email.split("@")[0].lower()).strip("-") or "workspace"
    slug = slug_base
    counter = 1
    while Tenant.objects.filter(slug=slug).exists():
        slug = f"{slug_base}-{counter}"
        counter += 1

    name = f"{instance.first_name or instance.email.split('@')[0]}'s Workspace"
    tenant = Tenant.objects.create(name=name, slug=slug, owner=instance)
    role = Role.objects.create(tenant=tenant, name="Owner", permissions={})
    Membership.objects.create(
        user=instance,
        tenant=tenant,
        role=role,
        status=Membership.StatusChoices.ACTIVE,
        joined_at=timezone.now(),
    )
    logger.info(f"Auto-bootstrapped workspace for {instance.email}")

