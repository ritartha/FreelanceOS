from django.contrib import admin

from apps.invoices.models import Invoice, InvoiceLineItem

admin.site.register(Invoice)
admin.site.register(InvoiceLineItem)
