from rest_framework import generics, permissions, viewsets

from apps.common.mixins import TenantQuerysetMixin
from apps.portfolio.api.serializers import PortfolioItemPublicSerializer, PortfolioItemSerializer
from apps.portfolio.models import PortfolioItem


class PortfolioItemViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = PortfolioItem.objects.all()
    serializer_class = PortfolioItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class PortfolioPublicDetailView(generics.RetrieveAPIView):
    queryset = PortfolioItem.objects.filter(is_published=True)
    serializer_class = PortfolioItemPublicSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"
