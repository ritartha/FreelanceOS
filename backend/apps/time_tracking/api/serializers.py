from rest_framework import serializers

from apps.time_tracking.models import TimeLog


class TimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = "__all__"
        read_only_fields = ["tenant", "created_by", "updated_by", "created_at", "updated_at", "deleted_at"]
