from django.contrib import admin

from apps.crm.models import Client, CommunicationHistory, Company, Contact, Tag

admin.site.register(Client)
admin.site.register(Contact)
admin.site.register(Company)
admin.site.register(Tag)
admin.site.register(CommunicationHistory)
