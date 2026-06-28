from django.contrib import admin

from apps.tenants.models import Membership, Role, Tenant

admin.site.register(Tenant)
admin.site.register(Role)
admin.site.register(Membership)
