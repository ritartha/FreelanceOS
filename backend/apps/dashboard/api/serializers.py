from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
    projects = serializers.IntegerField()
    tasks = serializers.IntegerField()
    invoices = serializers.IntegerField()
    expenses = serializers.IntegerField()
