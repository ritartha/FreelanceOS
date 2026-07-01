from django.contrib import admin

from apps.portfolio.models import PortfolioItem, PortfolioMedia

admin.site.register(PortfolioItem)
admin.site.register(PortfolioMedia)
