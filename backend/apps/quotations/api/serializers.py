from rest_framework import serializers

from apps.quotations.models import Quotation, QuotationLineItem, QuotationVersion

TENANT_AWARE_READ_ONLY = ["id", "tenant", "created_by", "updated_by", "created_at", "updated_at", "is_deleted", "deleted_at", "deleted_by", "metadata"]


class QuotationLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationLineItem
        fields = "__all__"
        read_only_fields = ["id", "total"]


class QuotationVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationVersion
        fields = "__all__"
        read_only_fields = TENANT_AWARE_READ_ONLY


class QuotationSerializer(serializers.ModelSerializer):
    line_items = QuotationLineItemSerializer(many=True, required=False)

    class Meta:
        model = Quotation
        fields = "__all__"
        read_only_fields = TENANT_AWARE_READ_ONLY + [
            "quotation_number", "subtotal", "discount_amount", "tax_amount", "total",
            "public_token", "sent_at", "accepted_at", "declined_at", "status",
        ]

    def create(self, validated_data):
        line_items_data = validated_data.pop("line_items", [])
        quotation = Quotation.objects.create(**validated_data)
        for item_data in line_items_data:
            QuotationLineItem.objects.create(quotation=quotation, **item_data)
        return quotation

    def update(self, instance, validated_data):
        line_items_data = validated_data.pop("line_items", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if line_items_data is not None:
            instance.line_items.all().delete()
            for item_data in line_items_data:
                QuotationLineItem.objects.create(quotation=instance, **item_data)

        return instance


class PublicQuotationSerializer(serializers.ModelSerializer):
    """Stripped-down read-only serializer for the unauthenticated public link."""

    line_items = QuotationLineItemSerializer(many=True, read_only=True)

    class Meta:
        model = Quotation
        fields = [
            "id", "quotation_number", "status", "issue_date", "valid_until",
            "subtotal", "discount_amount", "tax_rate", "tax_amount", "total",
            "currency", "notes", "line_items",
        ]
