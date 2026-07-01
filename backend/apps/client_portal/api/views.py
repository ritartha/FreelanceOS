from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.client_portal.api.serializers import (
    ClientPortalAccessSerializer,
    ClientPortalMessageSerializer,
    PortalLoginSerializer,
    PortalSetupSerializer,
)
from apps.client_portal.models import ClientPortalAccess, ClientPortalMessage
from apps.client_portal.permissions import IsPortalClient
from apps.client_portal.services.auth_service import (
    portal_login,
    send_portal_invite,
    set_portal_password,
)
from apps.common.mixins import TenantQuerysetMixin


# ── Auth ───────────────────────────────────────────────────────────────────────

class PortalLoginView(APIView):
    """POST /api/v1/portal/auth/login/  →  {access, refresh, client_id}"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PortalLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # tenant is resolved from subdomain/header by middleware;
        # fall back to query param for multi-tenant setups
        tenant = getattr(request, "tenant", None)
        if not tenant:
            from apps.tenants.models import Tenant
            tenant_id = request.data.get("tenant_id")
            if not tenant_id:
                return Response({"detail": "tenant_id is required."}, status=400)
            try:
                tenant = Tenant.objects.get(id=tenant_id, is_active=True)
            except Tenant.DoesNotExist:
                return Response({"detail": "Invalid tenant."}, status=400)

        try:
            tokens = portal_login(
                serializer.validated_data["email"],
                serializer.validated_data["password"],
                tenant,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(tokens)


class PortalSetupView(APIView):
    """POST /api/v1/portal/auth/setup/  →  {access, refresh, client_id}"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PortalSetupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            tokens = set_portal_password(
                str(serializer.validated_data["invite_token"]),
                serializer.validated_data["password"],
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(tokens)


# ── Freelancer-side: manage portal access ─────────────────────────────────────

class ClientPortalAccessViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    """
    Freelancer creates/manages portal access records for their clients.
    GET /api/v1/portal/access/               → list
    POST /api/v1/portal/access/              → create + optionally send invite
    POST /api/v1/portal/access/{id}/invite/  → (re)send invite email
    """
    queryset = ClientPortalAccess.objects.all()
    serializer_class = ClientPortalAccessSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        tenant = self._resolve_tenant()
        instance = serializer.save(tenant=tenant, created_by=self.request.user)
        if self.request.data.get("send_invite", True):
            base_url = self.request.data.get("base_url", "")
            try:
                send_portal_invite(instance, base_url=base_url)
            except Exception:
                pass  # invite send failure shouldn't break access creation

    @action(detail=True, methods=["post"], url_path="invite")
    def invite(self, request, pk=None):
        instance = self.get_object()
        base_url = request.data.get("base_url", "")
        try:
            send_portal_invite(instance, base_url=base_url)
        except Exception as e:
            return Response({"detail": str(e)}, status=500)
        return Response({"detail": "Invite sent."})


# ── Client-side: scoped read/write through portal JWT ─────────────────────────

class PortalMeView(APIView):
    """GET /api/v1/portal/me/  →  client profile"""
    permission_classes = [IsPortalClient]

    def get(self, request):
        from apps.crm.api.serializers import ClientSerializer
        return Response(ClientSerializer(request.portal_client).data)


class PortalProjectListView(generics.ListAPIView):
    """GET /api/v1/portal/projects/  →  projects for this client"""
    permission_classes = [IsPortalClient]

    def get_queryset(self):
        from apps.projects.models import Project
        return Project.objects.filter(
            client=self.request.portal_client, is_deleted=False
        )

    def get_serializer_class(self):
        from apps.projects.api.serializers import ProjectSerializer
        return ProjectSerializer


class PortalInvoiceListView(generics.ListAPIView):
    """GET /api/v1/portal/invoices/  →  invoices for this client"""
    permission_classes = [IsPortalClient]

    def get_queryset(self):
        from apps.invoices.models import Invoice
        return Invoice.objects.filter(
            client=self.request.portal_client, is_deleted=False
        ).exclude(status=Invoice.StatusChoices.DRAFT)

    def get_serializer_class(self):
        from apps.invoices.api.serializers import InvoiceSerializer
        return InvoiceSerializer


class PortalQuotationListView(generics.ListAPIView):
    """GET /api/v1/portal/quotations/  →  quotations for this client"""
    permission_classes = [IsPortalClient]

    def get_queryset(self):
        from apps.quotations.models import Quotation
        return Quotation.objects.filter(
            client=self.request.portal_client, is_deleted=False
        ).exclude(status=Quotation.StatusChoices.DRAFT)

    def get_serializer_class(self):
        from apps.quotations.api.serializers import QuotationSerializer
        return QuotationSerializer


class PortalQuotationAcceptView(APIView):
    """POST /api/v1/portal/quotations/{id}/accept/"""
    permission_classes = [IsPortalClient]

    def post(self, request, pk):
        from apps.quotations.models import Quotation
        from apps.quotations.services.email_service import accept_quotation
        from django.shortcuts import get_object_or_404
        quotation = get_object_or_404(Quotation, id=pk, client=request.portal_client)
        quotation = accept_quotation(quotation)
        from apps.quotations.api.serializers import QuotationSerializer
        return Response(QuotationSerializer(quotation).data)


class PortalFileListView(generics.ListAPIView):
    """GET /api/v1/portal/files/?project_id=<uuid>  →  files for this client"""
    permission_classes = [IsPortalClient]

    def get_queryset(self):
        from apps.files.models import FileAttachment
        qs = FileAttachment.objects.filter(
            entity_type="client",
            entity_id=self.request.portal_client.id,
            is_deleted=False,
        )
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = FileAttachment.objects.filter(
                entity_type="project",
                entity_id=project_id,
                is_deleted=False,
            )
        return qs

    def get_serializer_class(self):
        from apps.files.api.serializers import FileAttachmentSerializer
        return FileAttachmentSerializer


class PortalMessageListView(generics.ListCreateAPIView):
    """GET/POST /api/v1/portal/messages/"""
    permission_classes = [IsPortalClient]
    serializer_class = ClientPortalMessageSerializer

    def get_queryset(self):
        qs = ClientPortalMessage.objects.filter(
            client=self.request.portal_client, is_deleted=False
        )
        # Mark unread freelancer messages as read
        qs.filter(sender_type="freelancer", read_at__isnull=True).update(
            read_at=timezone.now()
        )
        return qs

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.portal_tenant,
            client=self.request.portal_client,
            sender_type="client",
            created_by=None,
        )


class PortalMilestoneApproveView(APIView):
    """POST /api/v1/portal/milestones/{id}/approve/"""
    permission_classes = [IsPortalClient]

    def post(self, request, pk):
        from apps.projects.models import Milestone
        from django.shortcuts import get_object_or_404
        milestone = get_object_or_404(
            Milestone, id=pk, project__client=request.portal_client
        )
        milestone.status = "approved"
        milestone.save(update_fields=["status", "updated_at"])
        return Response({"detail": "Milestone approved."})
