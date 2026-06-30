import uuid

from django.db import models

from apps.common.models import TenantAwareModel


class ProposalTemplate(TenantAwareModel):
    """
    Reusable proposal content. `body_markdown` may contain {{variable_name}}
    placeholders which get substituted at send-time using the Proposal's
    own `variable_values` plus any ProposalVariable defaults.
    """

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True)
    body_markdown = models.TextField(blank=True)
    is_favorite = models.BooleanField(default=False)

    class Meta:
        db_table = "proposals_template"

    def __str__(self):
        return self.name


class ProposalTemplateVersion(TenantAwareModel):
    """Snapshot of a template's content, written whenever the template is edited."""

    template = models.ForeignKey(ProposalTemplate, on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveIntegerField()
    body_markdown = models.TextField(blank=True)

    class Meta:
        db_table = "proposals_template_version"
        ordering = ["-version_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["template", "version_number"], name="uniq_template_version_number"
            )
        ]

    def __str__(self):
        return f"{self.template.name} v{self.version_number}"


class ProposalVariable(TenantAwareModel):
    """A reusable named placeholder, e.g. {{client_name}}, with a default value."""

    key = models.SlugField(max_length=100, help_text="Used in templates as {{key}}.")
    label = models.CharField(max_length=150, blank=True)
    default_value = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = "proposals_variable"
        constraints = [models.UniqueConstraint(fields=["tenant", "key"], name="uniq_tenant_variable_key")]

    def __str__(self):
        return self.key


class Proposal(TenantAwareModel):
    class StatusChoices(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        VIEWED = "viewed", "Viewed"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        EXPIRED = "expired", "Expired"

    client = models.ForeignKey("crm.Client", on_delete=models.CASCADE, related_name="proposals")
    template = models.ForeignKey(
        ProposalTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name="proposals"
    )
    title = models.CharField(max_length=255)
    body_markdown = models.TextField(blank=True, help_text="Final content after variable substitution.")
    variable_values = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.DRAFT)
    sent_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)
    public_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        db_table = "proposals_proposal"

    def __str__(self):
        return self.title


class ProposalView(TenantAwareModel):
    """One row per time the public proposal link is opened — powers analytics."""

    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name="views")
    viewed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = "proposals_view"
        ordering = ["-viewed_at"]

    def __str__(self):
        return f"View of {self.proposal} at {self.viewed_at}"
