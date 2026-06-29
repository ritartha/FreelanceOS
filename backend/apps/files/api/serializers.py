from rest_framework import serializers

from apps.files.models import FileAttachment


class FileAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileAttachment
        fields = "__all__"
        read_only_fields = ["tenant", "created_by", "updated_by", "created_at", "updated_at", "deleted_at"]
