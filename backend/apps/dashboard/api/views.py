from rest_framework.response import Response
from rest_framework.views import APIView


class DashboardSummaryAPIView(APIView):
    def get(self, request):
        return Response({"projects": 0, "tasks": 0, "invoices": 0, "expenses": 0})
