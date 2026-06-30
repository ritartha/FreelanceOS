from django.http import HttpResponse
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.mixins import TenantQuerysetMixin
from apps.proposals.api.serializers import (
    ProposalSerializer,
    ProposalTemplateSerializer,
    ProposalVariableSerializer,
)
from apps.proposals.api.serializers import PublicProposalSerializer
from apps.proposals.models import Proposal, ProposalTemplate, ProposalTemplateVersion, ProposalVariable
from apps.proposals.services.pdf_service import render_proposal_pdf
from apps.proposals.services.proposal_service import accept_proposal, decline_proposal, record_view
from apps.proposals.services.variable_service import render_variables


class ProposalTemplateViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = ProposalTemplate.objects.all()
    serializer_class = ProposalTemplateSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category=category)
        favorite = self.request.query_params.get("favorite")
        if favorite is not None:
            qs = qs.filter(is_favorite=favorite.lower() == "true")
        return qs

    def perform_update(self, serializer):
        """Snapshot the previous body as a version before saving the edit."""
        instance = self.get_object()
        next_version = instance.versions.count() + 1
        ProposalTemplateVersion.objects.create(
            tenant=instance.tenant,
            template=instance,
            version_number=next_version,
            body_markdown=instance.body_markdown,
            created_by=self.request.user,
        )
        serializer.save(updated_by=self.request.user)


class ProposalVariableViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = ProposalVariable.objects.all()
    serializer_class = ProposalVariableSerializer


class ProposalViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        client_id = self.request.query_params.get("client")
        if client_id:
            qs = qs.filter(client_id=client_id)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def perform_create(self, serializer):
        """Resolve {{variables}} into body_markdown at creation time."""
        tenant = self._resolve_tenant()
        template = serializer.validated_data.get("template")
        variable_values = serializer.validated_data.get("variable_values", {})
        body_markdown = serializer.validated_data.get("body_markdown") or (
            template.body_markdown if template else ""
        )
        rendered = render_variables(body_markdown, tenant, variable_values)
        serializer.save(tenant=tenant, created_by=self.request.user, body_markdown=rendered)

    @action(detail=True, methods=["post"], url_path="send")
    def send(self, request, pk=None):
        from apps.proposals.tasks import send_proposal_email_task

        proposal = self.get_object()
        recipient = request.data.get("recipient_email")
        send_proposal_email_task.delay(str(proposal.id), recipient)
        return Response({"detail": "Proposal email queued."})

    @action(detail=True, methods=["get"], url_path="pdf")
    def pdf(self, request, pk=None):
        proposal = self.get_object()
        pdf_bytes = render_proposal_pdf(proposal)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{proposal.title}.pdf"'
        return response

    @action(detail=True, methods=["get"], url_path="analytics")
    def analytics(self, request, pk=None):
        proposal = self.get_object()
        views = proposal.views.all()
        return Response(
            {
                "status": proposal.status,
                "sent_at": proposal.sent_at,
                "view_count": views.count(),
                "first_viewed_at": views.last().viewed_at if views.exists() else None,
                "last_viewed_at": views.first().viewed_at if views.exists() else None,
                "accepted_at": proposal.accepted_at,
                "declined_at": proposal.declined_at,
            }
        )


class PublicProposalView(APIView):
    """
    Unauthenticated endpoint backing the shareable proposal link:
        GET  /api/v1/public/proposals/<token>/          -> view (also logs a ProposalView)
        POST /api/v1/public/proposals/<token>/accept/    -> accept
        POST /api/v1/public/proposals/<token>/decline/   -> decline
    """

    permission_classes = [permissions.AllowAny]

    def get_object(self, token):
        from django.shortcuts import get_object_or_404

        return get_object_or_404(Proposal, public_token=token)

    def get(self, request, token):
        proposal = self.get_object(token)
        record_view(
            proposal,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return Response(PublicProposalSerializer(proposal).data)


class PublicProposalAcceptView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, token):
        from django.shortcuts import get_object_or_404

        proposal = get_object_or_404(Proposal, public_token=token)
        proposal = accept_proposal(proposal)
        return Response(PublicProposalSerializer(proposal).data)


class PublicProposalDeclineView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, token):
        from django.shortcuts import get_object_or_404

        proposal = get_object_or_404(Proposal, public_token=token)
        proposal = decline_proposal(proposal)
        return Response(PublicProposalSerializer(proposal).data)
