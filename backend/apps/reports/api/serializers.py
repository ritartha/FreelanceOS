from rest_framework import serializers


class ReportResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
