import uuid

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class Tenant(TimeStampedModel):
    class PlanChoices(models.TextChoices):
        FREE = "free", "Free"
        PRO = "pro", "Pro"
        ENTERPRISE = "enterprise", "Enterprise"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_tenants")
    plan = models.CharField(max_length=20, choices=PlanChoices.choices, default=PlanChoices.FREE)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "tenants_tenant"

    def __str__(self):
        return self.name


class Role(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="roles")
    name = models.CharField(max_length=100)
    permissions = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "tenants_role"
        constraints = [models.UniqueConstraint(fields=["tenant", "name"], name="uniq_tenant_role_name")]

    def __str__(self):
        return self.name


class Membership(TimeStampedModel):
    class StatusChoices(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        INVITED = "invited", "Invited"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="memberships")
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    joined_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tenants_membership"
        constraints = [models.UniqueConstraint(fields=["tenant", "user"], name="uniq_membership_tenant_user")]

    def __str__(self):
        return f"{self.user} @ {self.tenant}"
