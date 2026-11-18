from common.selectors.base import BaseSelector

from .models import Appointment


class AppointmentSelector(BaseSelector):
    """Query configuration for the ``Appointment`` model.

    Drives the generic list/retrieve filtering, search and ordering
    provided by ``BaseSelector`` (and consumed by ``BaseModelViewSet``).
    """

    model = Appointment

    searchable_fields = (
        "appointment_code",
        "user__name",
        "user__student_id",
        "user__email",
        "service__name",
    )

    select_related = (
        "user",
        "service",
        "slot",
        "slot__service",
    )

    ordering_fields = (
        "appointment_code",
        "status",
        "created_at",
        "updated_at",
    )

    default_ordering = ("-created_at",)

    filterable_fields = {
        "user": ("exact",),
        "service": ("exact",),
        "slot": ("exact",),
        "status": ("exact",),
        "appointment_code": ("exact", "icontains"),
        "created_at": ("date", "exact", "gte", "lte"),
        "updated_at": ("date", "exact", "gte", "lte"),
    }