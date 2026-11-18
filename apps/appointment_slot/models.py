from django.db import models
import uuid

from django.db.models import F, Q

class Status(models.TextChoices):
    AVAILABLE = "AVAILABLE", "Available"
    FULL = "FULL", "Full"
    INACTIVE = "INACTIVE", "Inactive"

class AppointmentSlot(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    service = models.ForeignKey(
        "services.DocumentService",
        on_delete=models.PROTECT,
        related_name="appointment_slots",
    )

    appointment_date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    capacity = models.PositiveIntegerField(
        default=1,
        help_text="Maximum number of appointments allowed for this slot",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "appointment_slots"
        ordering = ("appointment_date", "start_time")

        constraints = [
            models.CheckConstraint(
                condition=Q(end_time__gt=F("start_time")),
                name="appointment_slot_end_after_start",
            ),
            models.CheckConstraint(
                condition=Q(capacity__gt=0),
                name="appointment_slot_capacity_positive",
            ),
            models.UniqueConstraint(
                fields=[
                    "service",
                    "appointment_date",
                    "start_time",
                    "end_time",
                ],
                name="unique_service_slot",
            )
        ]

    indexes = [
        models.Index(
            fields=["appointment_date"],
            name="slot_date_idx",
        ),
        models.Index(
            fields=["service", "appointment_date"],
            name="slot_service_date_idx",
        ),
        models.Index(
            fields=["status"],
            name="slot_status_idx",
        ),
    ]

    def __str__(self):
        return (
            f"{self.service} | "
            f"{self.appointment_date} "
            f"{self.start_time}-{self.end_time}"
        )

    @property
    def slot_schedule(self):
        return (
            f"{self.appointment_date} "
            f"{self.start_time.strftime('%I:%M %p')} - "
            f"{self.end_time.strftime('%I:%M %p')}"
        )

    @property
    def remaining_capacity(self):
        from apps.appointments.models import Appointment

        return self.capacity - self.appointments.exclude(
            status=Appointment.Status.CANCELLED
        ).count()

    @property
    def update_status(self):
        if self.remaining_capacity <= 0:
            self.status = self.Status.FULL
        else:
            self.status = self.Status.AVAILABLE