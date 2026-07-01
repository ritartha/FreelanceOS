from django.db import models

from apps.common.models import TenantAwareModel


class PortfolioItem(TenantAwareModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    summary = models.TextField(blank=True)
    body_markdown = models.TextField(blank=True)
    client_name = models.CharField(max_length=255, blank=True)
    tags = models.JSONField(default=list)
    skills = models.JSONField(default=list)
    cover_image = models.ImageField(upload_to="portfolio/covers/", null=True, blank=True)
    is_published = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "portfolio_item"
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return self.title


class PortfolioMedia(models.Model):
    item = models.ForeignKey(PortfolioItem, on_delete=models.CASCADE, related_name="media")
    file = models.FileField(upload_to="portfolio/media/")
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "portfolio_media"
        ordering = ["order"]

    def __str__(self):
        return self.caption or f"Media {self.id}"
