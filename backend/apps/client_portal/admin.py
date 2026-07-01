from django.contrib import admin
from apps.client_portal.models import ClientPortalAccess, ClientPortalMessage

admin.site.register(ClientPortalAccess)
admin.site.register(ClientPortalMessage)
