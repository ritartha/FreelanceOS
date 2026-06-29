from rest_framework import serializers

from apps.tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["tenant", "created_by", "updated_by", "created_at", "updated_at", "deleted_at"]
