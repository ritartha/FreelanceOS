from rest_framework import serializers

from apps.portfolio.models import PortfolioItem, PortfolioMedia

TENANT_AWARE_READ_ONLY = [
    "id", "tenant", "created_by", "updated_by", "created_at", "updated_at",
    "is_deleted", "deleted_at", "deleted_by", "metadata",
]


class PortfolioMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioMedia
        fields = "__all__"


class PortfolioItemSerializer(serializers.ModelSerializer):
    media = PortfolioMediaSerializer(many=True, read_only=True)

    class Meta:
        model = PortfolioItem
        fields = "__all__"
        read_only_fields = TENANT_AWARE_READ_ONLY


class PortfolioItemPublicSerializer(serializers.ModelSerializer):
    media = PortfolioMediaSerializer(many=True, read_only=True)

    class Meta:
        model = PortfolioItem
        fields = [
            "title", "slug", "summary", "body_markdown",
            "client_name", "tags", "skills", "cover_image", "media",
        ]
