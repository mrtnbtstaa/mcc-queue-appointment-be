from django.db import models

from common.models.timestamp_model import TimestampModel
import uuid

class Transaction(TimestampModel):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.PROTECT,
        related_name="transactions",
    )

    processed_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="processed_transactions",
    )

    transaction_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    remarks = models.TextField(
        null=True,
        blank=True,
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Transaction #{self.pk} - {self.transaction_status}"