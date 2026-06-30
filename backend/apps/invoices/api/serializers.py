from rest_framework import serializers

from apps.invoices.models import Invoice, InvoiceLineItem


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = "__all__"
        read_only_fields = ["id", "tenant", "created_by", "updated_by", "created_at", "updated_at", "is_deleted", "deleted_at", "deleted_by", "metadata"]

    def create(self, validated_data):
        """Auto-generate invoice_number if not supplied by the user."""
        if not validated_data.get("invoice_number"):
            tenant = validated_data.get("tenant")
            validated_data["invoice_number"] = Invoice.generate_invoice_number(tenant)
        return super().create(validated_data)


class InvoiceLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLineItem
        fields = "__all__"
        read_only_fields = ["id"]
