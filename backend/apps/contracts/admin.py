from django.contrib import admin

from apps.contracts.models import Contract, ContractVersion

admin.site.register(Contract)
admin.site.register(ContractVersion)
