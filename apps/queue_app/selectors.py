
from common.selectors.base import BaseSelector

from .models import Queue


class QueueSelector(BaseSelector):
    """Query configuration for queue list and retrieve operations."""

    model = Queue

    searchable_fields = (
        "queue_number",
        "appointment__appointment_code",
        "appointment__user__email",
        "appointment__user__name",
        "appointment__user__student_id",
        "appointment__service__name",
    )

    select_related = (
        "appointment",
        "appointment__user",
        "appointment__service",
        "appointment__slot",
    )

    ordering_fields = (
        "queue_number",
        "queue_date",
        "status",
        "called_at",
        "completed_at",
        "created_at",
        "updated_at",
    )

    default_ordering = ("queue_date", "queue_number")

    filterable_fields = {
        "appointment": ("exact",),
        "queue_number": ("exact", "icontains"),
        "queue_date": ("exact", "gte", "lte"),
        "status": ("exact",),
        "created_at": ("date", "exact", "gte", "lte"),
        "updated_at": ("date", "exact", "gte", "lte"),
    }
