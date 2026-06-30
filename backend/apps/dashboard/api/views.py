from rest_framework.response import Response
from rest_framework.views import APIView


class DashboardSummaryAPIView(APIView):
    def get(self, request):
        tenant = getattr(request, "tenant", None)

        if not tenant:
            # Fallback: resolve tenant from JWT-authenticated user
            if request.user and request.user.is_authenticated:
                from apps.tenants.models import Membership
                membership = Membership.objects.filter(
                    user=request.user,
                    status="active",
                    tenant__is_active=True,
                ).order_by("-created_at").first()
                if membership:
                    tenant = membership.tenant

        if not tenant:
            return Response({"projects": 0, "tasks": 0, "invoices": 0, "expenses": 0})

        from apps.projects.models import Project
        from apps.tasks.models import Task
        from apps.invoices.models import Invoice
        from apps.expenses.models import Expense

        projects = Project.objects.filter(tenant=tenant, status="active").count()
        tasks = Task.objects.filter(tenant=tenant).exclude(status__in=["done", "cancelled"]).count()
        invoices = Invoice.objects.filter(tenant=tenant).exclude(status__in=["paid", "cancelled"]).count()
        expenses = Expense.objects.filter(tenant=tenant).count()

        return Response({
            "projects": projects,
            "tasks": tasks,
            "invoices": invoices,
            "expenses": expenses,
        })
