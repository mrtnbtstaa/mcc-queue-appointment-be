import uuid

from django.conf import settings
from django.db import models

from common.models.timestamp_model import TimestampModel


class NotificationCategory(models.TextChoices):
    APPOINTMENT = "APPOINTMENT", "Appointment"
    TRANSACTION = "TRANSACTION", "Transaction"
    QUEUE = "QUEUE", "Queue"


class Notification(TimestampModel):
    """In-app alert delivered to a single user."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    category = models.CharField(
        max_length=20,
        choices=NotificationCategory.choices,
    )

    title = models.CharField(max_length=120)

    message = models.TextField()

    # PK of the appointment / transaction / queue this alert refers to.
    reference_id = models.UUIDField(null=True, blank=True)

    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} -> {self.user_id}"
