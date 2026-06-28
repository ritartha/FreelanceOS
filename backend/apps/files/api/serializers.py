from rest_framework import serializers

from apps.files.models import FileAttachment


class FileAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileAttachment
        fields = "__all__"
