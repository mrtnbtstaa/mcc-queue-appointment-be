from common.selectors.base import BaseSelector
from .models import AppointmentSlot


class AppointmentSlotSelector(BaseSelector):

    model = AppointmentSlot

    searchable_fields = ("service__name",)

    ordering_fields = (
        "appointment_date",
        "start_time",
        "end_time",
        "capacity",
        "created_at",
    )

    default_ordering = ("appointment_date", "start_time")

    filterable_fields = {
        "service": ("exact",),
        "appointment_date": ("exact", "gte", "lte"),
        "start_time": ("exact", "gte", "lte"),
        "end_time": ("exact", "gte", "lte"),
        "capacity": ("exact", "gte", "lte"),
        "status": ("exact",),
        "created_at": ("date", "exact", "gte", "lte"),
    }