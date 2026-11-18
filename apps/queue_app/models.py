
from django.db import models
from common.models.timestamp_model import TimestampModel
import uuid

class QueueStatus(models.TextChoices):
    WAITING = "WAITING", "Waiting"
    SERVING = "SERVING", "Serving"
    COMPLETED = "COMPLETED", "Completed"
    SKIPPED = "SKIPPED", "Skipped"


class QueueCounter(models.Model):
    """
    Internal daily sequence generator.
    One counter per queue date.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    queue_date = models.DateField(unique=True)
    next_number = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "queue_counters"


class Queue(TimestampModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    appointment = models.OneToOneField(
        "appointments.Appointment",
        on_delete=models.PROTECT,
        related_name="queue",
        db_column="appointment_id",
    )

    queue_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    queue_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=QueueStatus.choices,
        default=QueueStatus.WAITING,
    )

    called_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )


    class Meta:
        db_table = "queues"

        ordering = ("queue_date", "queue_number")

        indexes = [
            models.Index(
                fields=["queue_date", "status"],
                name="queue_date_status_idx",
            ),
        ]

    def __str__(self):
        return self.queue_number
