from rest_framework import serializers

from apps.files.models import FileAttachment, FileTag, FileVersion, Folder


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = "__all__"
        read_only_fields = ["id", "tenant", "created_by", "updated_by", "created_at", "updated_at", "is_deleted", "deleted_at", "deleted_by", "metadata"]


class FileTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileTag
        fields = "__all__"
        read_only_fields = ["id", "tenant", "created_by", "updated_by", "created_at", "updated_at", "is_deleted", "deleted_at", "deleted_by", "metadata"]


class FileVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileVersion
        fields = "__all__"
        read_only_fields = ["id", "tenant", "created_by", "updated_by", "created_at", "updated_at", "is_deleted", "deleted_at", "deleted_by", "metadata"]


class FileAttachmentSerializer(serializers.ModelSerializer):
    versions = FileVersionSerializer(many=True, read_only=True)

    class Meta:
        model = FileAttachment
        fields = "__all__"
        read_only_fields = ["id", "tenant", "created_by", "updated_by", "created_at", "updated_at", "is_deleted", "deleted_at", "deleted_by", "metadata", "size", "current_version"]
