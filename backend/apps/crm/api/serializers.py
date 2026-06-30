from rest_framework import serializers

from apps.crm.models import Client, CommunicationHistory, Company, Contact, Tag


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"
        read_only_fields = ["id", "tenant", "created_by", "updated_by", "created_at", "updated_at", "is_deleted", "deleted_at", "deleted_by", "metadata"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = ["id", "tenant", "created_by", "updated_by", "created_at", "updated_at", "is_deleted", "deleted_at", "deleted_by", "metadata"]


class CommunicationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationHistory
        fields = "__all__"
        read_only_fields = ["id", "tenant", "created_by", "updated_by", "created_at", "updated_at", "is_deleted", "deleted_at", "deleted_by", "metadata"]


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"
        read_only_fields = ["id", "tenant", "created_by", "updated_by", "created_at", "updated_at", "is_deleted", "deleted_at", "deleted_by", "metadata", "lead_score"]


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"
        read_only_fields = ["id", "tenant", "created_by", "updated_by", "created_at", "updated_at", "is_deleted", "deleted_at", "deleted_by", "metadata"]
