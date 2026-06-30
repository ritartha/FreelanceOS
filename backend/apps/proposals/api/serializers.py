from rest_framework import serializers

from apps.proposals.models import (
    Proposal,
    ProposalTemplate,
    ProposalTemplateVersion,
    ProposalVariable,
    ProposalView,
)
from apps.proposals.services.variable_service import extract_variable_keys

TENANT_AWARE_READ_ONLY = ["id", "tenant", "created_by", "updated_by", "created_at", "updated_at", "is_deleted", "deleted_at", "deleted_by", "metadata"]


class ProposalTemplateVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalTemplateVersion
        fields = "__all__"
        read_only_fields = TENANT_AWARE_READ_ONLY


class ProposalTemplateSerializer(serializers.ModelSerializer):
    versions = ProposalTemplateVersionSerializer(many=True, read_only=True)
    variable_keys = serializers.SerializerMethodField()

    class Meta:
        model = ProposalTemplate
        fields = "__all__"
        read_only_fields = TENANT_AWARE_READ_ONLY

    def get_variable_keys(self, obj):
        return extract_variable_keys(obj.body_markdown)


class ProposalVariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalVariable
        fields = "__all__"
        read_only_fields = TENANT_AWARE_READ_ONLY


class ProposalViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalView
        fields = "__all__"
        read_only_fields = TENANT_AWARE_READ_ONLY


class ProposalSerializer(serializers.ModelSerializer):
    view_count = serializers.SerializerMethodField()

    class Meta:
        model = Proposal
        fields = "__all__"
        read_only_fields = TENANT_AWARE_READ_ONLY + [
            "status", "sent_at", "accepted_at", "declined_at", "public_token",
        ]

    def get_view_count(self, obj):
        return obj.views.count()


class PublicProposalSerializer(serializers.ModelSerializer):
    """Stripped-down read-only serializer for the unauthenticated public link."""

    class Meta:
        model = Proposal
        fields = ["id", "title", "body_markdown", "status", "expires_at"]
