from common.selectors.base import BaseSelector

from .models import Transaction


class TransactionSelector(BaseSelector):
    """Query configuration for the Transaction model."""

    model = Transaction

    searchable_fields = (
        "appointment__appointment_code",
        "appointment__user__name",
        "appointment__user__student_id",
        "appointment__user__email",
        "appointment__service__name",
        "processed_by__name",
        "processed_by__email",
        "remarks",
    )

    select_related = (
        "appointment",
        "appointment__user",
        "appointment__service",
        "appointment__slot",
        "appointment__queue",
        "processed_by",
    )

    ordering_fields = (
        "transaction_status",
        "processed_at",
        "created_at",
        "updated_at",
    )

    default_ordering = ("-created_at",)

    filterable_fields = {
        "appointment": ("exact",),
        "processed_by": ("exact",),
        "transaction_status": ("exact",),
        "processed_at": ("date", "exact", "gte", "lte"),
        "created_at": ("date", "exact", "gte", "lte"),
        "updated_at": ("date", "exact", "gte", "lte"),
    }