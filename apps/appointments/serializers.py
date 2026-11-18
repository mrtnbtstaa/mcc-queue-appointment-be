import uuid

from rest_framework import serializers
from django.db import transaction
from apps.appointment_slot.models import AppointmentSlot, Status
from apps.queue_app.serializers import QueueWriteSerializer
from apps.services.models import DocumentService
from common.serializers.fields import RequiredCharField
from .models import Appointment


class AppointmentListSerializer(serializers.ModelSerializer):
    """Read serializer used for ``list`` / ``retrieve`` and as the
    response body of the ``set_status`` action."""

    user_name = serializers.CharField(
        source="user.name",
        read_only=True,
    )

    user_email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    student_id = serializers.CharField(
        source="user.student_id",
        read_only=True,
    )

    course = serializers.CharField(
        source="user.course",
        read_only=True,
    )

    year_level = serializers.CharField(
        source="user.year_level",
        read_only=True,
    )

    service_name = serializers.CharField(
        source="service.name",
        read_only=True,
    )

    slot_label = serializers.CharField(
        source="slot.__str__",
        read_only=True,
    )

    slot_schedule = serializers.CharField(
        source="slot.slot_schedule",
        read_only=True,
    )

    # status_display = serializers.CharField(
    #     source="get_status_display",
    #     read_only=True,
    # )

    class Meta:
        model = Appointment
        fields = (
            "id",
            "user",
            "user_name",
            "user_email",
            "student_id",
            "course",
            "year_level",
            "service",
            "service_name",
            "slot",
            "slot_label",
            "slot_schedule",
            "appointment_code",
            "status",
            # "status_display",
        )


class AppointmentWriteSerializer(serializers.ModelSerializer):
    """Write serializer used for ``create`` / ``update`` / ``partial_update``.

    ``user`` and ``appointment_code`` are intentionally read-only on input:
      * ``user`` is injected in ``ViewSet.perform_create`` from the request
        (so callers cannot spoof a different student).
      * ``appointment_code`` is generated server-side inside ``create``.
    """

    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    service = serializers.SlugRelatedField(
        slug_field="name",
        queryset=DocumentService.objects.all(),
        label="Service Name",
    )

    slot = serializers.PrimaryKeyRelatedField(
        queryset=AppointmentSlot.objects.all(),
        label="Appointment Slot",
    )

    appointment_code = serializers.CharField(
        read_only=True,
    )

    status = RequiredCharField(
        label="Appointment Status",
    )

    class Meta:
        model = Appointment
        fields = (
            "user",
            "service",
            "slot",
            "appointment_code",
            "status",
        )

    # ---- field-level validation -----------------------------------------

    def validate_slot(self, slot):
        if slot.status not in (Status.AVAILABLE, "Open"):
            raise serializers.ValidationError(
                "Selected slot is not available for booking."
            )
        if slot.remaining_capacity <= 0:
            raise serializers.ValidationError(
                "Selected slot is already full."
            )
        return slot

    def validate_status(self, status):
        if status not in Appointment.Status.values:
            raise serializers.ValidationError(
                "Invalid appointment status."
            )
        return status

    # ---- object-level validation ----------------------------------------

    def validate(self, attrs):
        slot = attrs.get("slot", getattr(self.instance, "slot", None))
        service = attrs.get("service", getattr(self.instance, "service", None))

        if slot and service and slot.service_id != service.id:
            raise serializers.ValidationError(
                {
                    "slot": [
                        "Selected slot does not belong to the requested service."
                    ]
                }
            )
        return attrs

    # ---- create ---------------------------------------------------------

    def create(self, validated_data):
        validated_data["appointment_code"] = self._generate_code()
        return super().create(validated_data)

    @staticmethod
    def _generate_code() -> str:
        # ``appointment_code`` is VARCHAR(30). ``APT-`` + 12 hex chars = 16 chars.
        return f"APT-{uuid.uuid4().hex[:12].upper()}"


class AppointmentStatusSerializer(serializers.ModelSerializer):
    """Used by the ``set_status`` action — only the ``status`` field
    can be patched through this endpoint."""

    status = serializers.ChoiceField(
        choices=Appointment.Status.choices,
        required=True,
        label="Appointment Status",
    )

    class Meta:
        model = Appointment
        fields = ("status",)

    @transaction.atomic
    def update(self, instance, validated_data):

        status = validated_data.get("status")

        if status == Appointment.Status.CONFIRMED and instance.status != Appointment.Status.CONFIRMED:
            QueueWriteSerializer().create({
                "appointment": instance
            })

        instance.status = status
        instance.save()

        return instance
