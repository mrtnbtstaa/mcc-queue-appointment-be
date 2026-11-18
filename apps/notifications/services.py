from __future__ import annotations

from .models import Notification, NotificationCategory


class NotificationService:
    @classmethod
    def notify_status_change(
        cls,
        *,
        user,
        category: str,
        reference_id,
        reference_label: str,
        status_display: str,
    ) -> Notification:
        label = NotificationCategory(category).label

        return Notification.objects.create(
            user=user,
            category=category,
            title=f"{label} status updated",
            message=f"{reference_label} is now {status_display}.",
            reference_id=reference_id,
        )
