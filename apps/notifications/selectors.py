from common.selectors.base import BaseSelector

from .models import Notification


class NotificationSelector(BaseSelector):
    """Query configuration for the authenticated user's inbox."""

    model = Notification

    searchable_fields = (
        "title",
        "message",
    )

    select_related = ("user",)

    ordering_fields = (
        "created_at",
        "is_read",
    )

    default_ordering = ("-created_at",)

    filterable_fields = {
        "category": ("exact",),
        "is_read": ("exact",),
        "created_at": ("date", "exact", "gte", "lte"),
    }
