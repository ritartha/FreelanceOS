from rest_framework import viewsets

from apps.calendar_app.api.serializers import CalendarEventSerializer
from apps.calendar_app.models import CalendarEvent
from apps.common.mixins import TenantQuerysetMixin


class CalendarEventViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = CalendarEvent.objects.all()
    serializer_class = CalendarEventSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        event_type = self.request.query_params.get("event_type")
        if event_type:
            qs = qs.filter(event_type=event_type)
        start_after = self.request.query_params.get("start_after")
        if start_after:
            qs = qs.filter(start__gte=start_after)
        start_before = self.request.query_params.get("start_before")
        if start_before:
            qs = qs.filter(start__lte=start_before)
        return qs
