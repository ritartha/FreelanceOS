from django.contrib import admin

from apps.quotations.models import Quotation, QuotationLineItem, QuotationVersion

admin.site.register(Quotation)
admin.site.register(QuotationLineItem)
admin.site.register(QuotationVersion)
