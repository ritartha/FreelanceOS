from django.contrib import admin

from apps.crm.models import Client, Contact

admin.site.register(Client)
admin.site.register(Contact)
