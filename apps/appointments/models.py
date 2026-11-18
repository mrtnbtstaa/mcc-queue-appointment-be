from django.conf import settings
from django.db import models
import uuid

from common.models.timestamp_model import TimestampModel
class Appointment(TimestampModel):
    """
    Records a student's booking of an academic-service appointment slot.

    Mirrors the ``appointments`` table:
        appointment_id   BIGINT   PK
        user_id          BIGINT   FK  -> the student who booked
        service_id       BIGINT   FK  -> the academic service requested
        slot_id          BIGINT   FK  -> the chosen appointment slot
        appointment_code VARCHAR(30)  UNIQUE  -> human-readable reference
        status           ENUM        -> PENDING / CONFIRMED / COMPLETED / CANCELLED
        created_at       DATETIME
        updated_at       DATETIME
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # user_id  -> FK to the logged-in student
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments",
        verbose_name="Student",
    )

    # service_id -> FK to the requested DocumentService
    service = models.ForeignKey(
        "services.DocumentService",
        on_delete=models.PROTECT,
        related_name="appointments",
        verbose_name="Service",
    )

    # slot_id -> FK to the chosen AppointmentSlot
    slot = models.ForeignKey(
        "appointment_slot.AppointmentSlot",
        on_delete=models.PROTECT,
        related_name="appointments",
        verbose_name="Appointment Slot",
    )

    appointment_code = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        verbose_name="Appointment Code",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Status",
    )

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["appointment_code"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.appointment_code} ({self.get_status_display()})"