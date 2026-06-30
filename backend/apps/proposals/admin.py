from django.contrib import admin

from apps.proposals.models import (
    Proposal,
    ProposalTemplate,
    ProposalTemplateVersion,
    ProposalVariable,
    ProposalView,
)

admin.site.register(Proposal)
admin.site.register(ProposalTemplate)
admin.site.register(ProposalTemplateVersion)
admin.site.register(ProposalVariable)
admin.site.register(ProposalView)
