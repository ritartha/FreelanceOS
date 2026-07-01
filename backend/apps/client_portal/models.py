"""
Client Portal auth model.

A ClientPortalAccess row is created by the freelancer for each client
they want to give portal access to. The client gets an email with a
magic-link or sets a password — they never need a full User account.

Auth flow:
  1. Freelancer creates ClientPortalAccess for a crm.Client.
  2. System sends an invite email with a one-time setup link.
  3. Client sets a password (stored here, not on User) OR uses a
     magic-link token to authenticate.
  4. On login, client_portal.services.auth_service issues a JWT with
     a custom claim: {"portal_client_id": "<uuid>"} so the portal
     permission class can identify and scope the request.
"""

import uuid

from django.db import models

from apps.common.models import TenantAwareModel


class ClientPortalAccess(TenantAwareModel):
    """
    Grants a crm.Client access to the Client Portal.
    One row per client per tenant — a client can have access to multiple
    tenants if multiple freelancers invite them (separate rows, separate tokens).
    """

    client = models.OneToOneField(
        "crm.Client", on_delete=models.CASCADE, related_name="portal_access"
    )
    email = models.EmailField(help_text="Login email for the portal (usually same as crm.Client.email).")
    password_hash = models.CharField(max_length=255, blank=True, help_text="Argon2/bcrypt hash of the portal password.")
    is_active = models.BooleanField(default=True)
    last_login_at = models.DateTimeField(null=True, blank=True)

    # Invite / setup token (one-time, expires after use or 7 days)
    invite_token = models.UUIDField(default=uuid.uuid4, unique=True)
    invite_sent_at = models.DateTimeField(null=True, blank=True)
    invite_accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "client_portal_access"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "email"], name="uniq_portal_email_per_tenant")
        ]

    def __str__(self):
        return f"Portal access for {self.client} ({self.email})"


class ClientPortalMessage(TenantAwareModel):
    """
    Simple messaging between the client and the freelancer through the portal.
    Not a full chat system — just a threaded message log per project.
    """

    client = models.ForeignKey("crm.Client", on_delete=models.CASCADE, related_name="portal_messages")
    project = models.ForeignKey(
        "projects.Project", on_delete=models.SET_NULL, null=True, blank=True, related_name="portal_messages"
    )
    sender_type = models.CharField(
        max_length=10, choices=[("client", "Client"), ("freelancer", "Freelancer")], default="client"
    )
    body = models.TextField()
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "client_portal_message"
        ordering = ["created_at"]

    def __str__(self):
        return f"Message from {self.sender_type} on {self.created_at:%Y-%m-%d}"
