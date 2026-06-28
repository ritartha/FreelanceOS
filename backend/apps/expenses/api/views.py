from rest_framework import viewsets

from apps.common.mixins import TenantQuerysetMixin
from apps.expenses.api.serializers import ExpenseSerializer
from apps.expenses.models import Expense


class ExpenseViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Expense.all_objects.all()
    serializer_class = ExpenseSerializer
