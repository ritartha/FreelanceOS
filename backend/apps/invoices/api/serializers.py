from rest_framework import serializers

from apps.invoices.models import Invoice, InvoiceLineItem, Payment, RecurringInvoice, RecurringInvoiceLineItem

TENANT_AWARE_READ_ONLY = [
    "id", "tenant", "created_by", "updated_by", "created_at", "updated_at",
    "is_deleted", "deleted_at", "deleted_by", "metadata",
]


class InvoiceLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLineItem
        fields = "__all__"
        read_only_fields = ["id", "total"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = TENANT_AWARE_READ_ONLY


class RecurringInvoiceLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringInvoiceLineItem
        fields = "__all__"
        read_only_fields = ["id"]


class RecurringInvoiceSerializer(serializers.ModelSerializer):
    line_items = RecurringInvoiceLineItemSerializer(many=True, required=False)

    class Meta:
        model = RecurringInvoice
        fields = "__all__"
        read_only_fields = TENANT_AWARE_READ_ONLY

    def create(self, validated_data):
        line_items_data = validated_data.pop("line_items", [])
        recurring = RecurringInvoice.objects.create(**validated_data)
        for item in line_items_data:
            RecurringInvoiceLineItem.objects.create(recurring_invoice=recurring, **item)
        return recurring


class InvoiceSerializer(serializers.ModelSerializer):
    line_items = InvoiceLineItemSerializer(many=True, required=False)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = "__all__"
        read_only_fields = TENANT_AWARE_READ_ONLY + [
            "invoice_number", "subtotal", "discount_amount", "tax_amount",
            "total", "amount_paid", "amount_due", "status", "paid_at", "sent_at",
        ]

    def create(self, validated_data):
        line_items_data = validated_data.pop("line_items", [])
        invoice = Invoice.objects.create(**validated_data)
        for item in line_items_data:
            InvoiceLineItem.objects.create(invoice=invoice, **item)
        return invoice

    def update(self, instance, validated_data):
        line_items_data = validated_data.pop("line_items", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if line_items_data is not None:
            instance.line_items.all().delete()
            for item in line_items_data:
                InvoiceLineItem.objects.create(invoice=instance, **item)
        return instance
