from rest_framework.routers import DefaultRouter

from apps.proposals.api.views import ProposalTemplateViewSet, ProposalVariableViewSet, ProposalViewSet

app_name = "proposals"

router = DefaultRouter()
router.register("templates", ProposalTemplateViewSet, basename="proposal-template")
router.register("variables", ProposalVariableViewSet, basename="proposal-variable")
router.register("", ProposalViewSet, basename="proposal")

urlpatterns = router.urls
