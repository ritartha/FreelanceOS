from rest_framework import serializers

from apps.client_portal.models import ClientPortalAccess, ClientPortalMessage

TENANT_AWARE_READ_ONLY = [
    "id", "tenant", "created_by", "updated_by", "created_at", "updated_at",
    "is_deleted", "deleted_at", "deleted_by", "metadata",
]


class ClientPortalAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientPortalAccess
        fields = "__all__"
        read_only_fields = TENANT_AWARE_READ_ONLY + [
            "password_hash", "invite_token", "invite_sent_at",
            "invite_accepted_at", "last_login_at",
        ]


class ClientPortalMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientPortalMessage
        fields = "__all__"
        read_only_fields = TENANT_AWARE_READ_ONLY + ["sender_type", "read_at"]


class PortalLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class PortalSetupSerializer(serializers.Serializer):
    invite_token = serializers.UUIDField()
    password = serializers.CharField(write_only=True, min_length=8)
