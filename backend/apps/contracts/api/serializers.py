from rest_framework import serializers

from apps.contracts.models import Contract, ContractVersion

TENANT_AWARE_READ_ONLY = [
    "id", "tenant", "created_by", "updated_by", "created_at", "updated_at",
    "is_deleted", "deleted_at", "deleted_by", "metadata",
]


class ContractVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractVersion
        fields = "__all__"
        read_only_fields = TENANT_AWARE_READ_ONLY


class ContractSerializer(serializers.ModelSerializer):
    is_expiring_soon = serializers.BooleanField(read_only=True)

    class Meta:
        model = Contract
        fields = "__all__"
        read_only_fields = TENANT_AWARE_READ_ONLY + [
            "status", "signed_at", "sent_at",
            "expiry_reminder_sent", "renewal_reminder_sent",
        ]
