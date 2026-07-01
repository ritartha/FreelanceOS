from rest_framework import serializers

from apps.calendar_app.models import CalendarEvent

TENANT_AWARE_READ_ONLY = [
    "id", "tenant", "created_by", "updated_by", "created_at", "updated_at",
    "is_deleted", "deleted_at", "deleted_by", "metadata",
]


class CalendarEventSerializer(serializers.ModelSerializer):
    source_label = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CalendarEvent
        fields = "__all__"
        read_only_fields = TENANT_AWARE_READ_ONLY

    def get_source_label(self, obj):
        if obj.task_id:
            return str(obj.task)
        if obj.project_id:
            return str(obj.project)
        if obj.invoice_id:
            return str(obj.invoice)
        if obj.contract_id:
            return str(obj.contract)
        return None
