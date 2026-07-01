from django.urls import path

from apps.reports.api.views import (
    ExportCSVView,
    ExportPDFView,
    ExpenseSummaryView,
    MonthlyExpensesView,
    MonthlyRevenueView,
    MonthlyTrendsView,
    ProfitSummaryView,
    RevenueSummaryView,
    TaxSummaryView,
    TopClientsView,
)

app_name = "reports"

urlpatterns = [
    path("revenue/", RevenueSummaryView.as_view(), name="revenue"),
    path("revenue/monthly/", MonthlyRevenueView.as_view(), name="revenue-monthly"),
    path("expenses/", ExpenseSummaryView.as_view(), name="expenses"),
    path("expenses/monthly/", MonthlyExpensesView.as_view(), name="expenses-monthly"),
    path("profit/", ProfitSummaryView.as_view(), name="profit"),
    path("tax/", TaxSummaryView.as_view(), name="tax"),
    path("top-clients/", TopClientsView.as_view(), name="top-clients"),
    path("trends/", MonthlyTrendsView.as_view(), name="trends"),
    path("export/csv/", ExportCSVView.as_view(), name="export-csv"),
    path("export/pdf/", ExportPDFView.as_view(), name="export-pdf"),
]
