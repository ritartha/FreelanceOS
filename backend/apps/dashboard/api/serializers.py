from rest_framework import serializers


class UpcomingDeadlineSerializer(serializers.Serializer):
    type  = serializers.CharField()
    title = serializers.CharField()
    due   = serializers.CharField()
    id    = serializers.CharField()


class RecentClientSerializer(serializers.Serializer):
    id         = serializers.CharField()
    name       = serializers.CharField()
    created_at = serializers.CharField()


class DashboardSummarySerializer(serializers.Serializer):
    projects                = serializers.IntegerField()
    tasks                   = serializers.IntegerField()
    invoices                = serializers.IntegerField()
    expenses                = serializers.IntegerField()
    revenue_this_month      = serializers.CharField()
    revenue_last_month      = serializers.CharField()
    revenue_delta_pct       = serializers.FloatField()
    outstanding_amount      = serializers.CharField()
    overdue_invoices        = serializers.IntegerField()
    upcoming_deadlines      = UpcomingDeadlineSerializer(many=True)
    recent_clients          = RecentClientSerializer(many=True)
    contracts_expiring_soon = serializers.IntegerField()
