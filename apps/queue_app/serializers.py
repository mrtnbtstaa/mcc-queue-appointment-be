
from django.db import transaction
from django.utils import timezone

from rest_framework import serializers

from apps.appointments.models import Appointment
from apps.users.models import UserRole


from .models import Queue, QueueCounter, QueueStatus


class QueueListSerializer(serializers.ModelSerializer):

    appointment_code = serializers.CharField(
        source="appointment.appointment_code",
        read_only=True,
    )

    service_name = serializers.CharField(
        source="appointment.service.name",
        read_only=True,
    )

    slot_schedule = serializers.CharField(
        source="appointment.slot.slot_schedule",
        read_only=True,
    )

    student_name = serializers.SerializerMethodField()
    student_id = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    year_level = serializers.SerializerMethodField()
    is_mine = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()

    class Meta:
        model = Queue

        fields = (
            "id",
            "appointment",
            "appointment_code",
            "student_name",
            "student_id",
            "course",
            "year_level",
            "service_name",
            "slot_schedule",
            "queue_number",
            "queue_date",
            "status",
            "position",
            "is_mine",
            "called_at",
            "completed_at",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def _is_staff_viewer(self):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return True
        return user.role == UserRole.STAFF or user.is_staff

    def _is_own_row(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return bool(
            user and user.is_authenticated
            and obj.appointment.user_id == user.id
        )

    def get_student_name(self, obj):
        if not self._is_staff_viewer() and not self._is_own_row(obj):
            return ""
        return obj.appointment.user.name or obj.appointment.user.email

    def get_student_id(self, obj):
        if not self._is_staff_viewer() and not self._is_own_row(obj):
            return ""
        return obj.appointment.user.student_id or ""

    def get_course(self, obj):
        if not self._is_staff_viewer() and not self._is_own_row(obj):
            return ""
        return obj.appointment.user.course or ""

    def get_year_level(self, obj):
        if not self._is_staff_viewer() and not self._is_own_row(obj):
            return ""
        return obj.appointment.user.year_level or ""

    def get_is_mine(self, obj):
        return self._is_own_row(obj)

    def get_position(self, obj):
        if obj.status == QueueStatus.SERVING:
            return 0
        if obj.status != QueueStatus.WAITING:
            return 0
        return (
            Queue.objects.filter(
                queue_date=obj.queue_date,
                status=QueueStatus.WAITING,
                queue_number__lt=obj.queue_number,
            ).count()
            + 1
        )


class QueueWriteSerializer(serializers.ModelSerializer):

    appointment = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all(),
        required=True,
    )

    queue_number = serializers.CharField(read_only=True)
    queue_date = serializers.DateField(read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Queue

        fields = (
            "appointment",
            "queue_number",
            "queue_date",
            "status",
        )

        read_only_fields = (
            "queue_number",
            "queue_date",
            "status",
        )

    def validate_appointment(self, appointment):
        if Queue.objects.filter(
            appointment=appointment
        ).exists():
            raise serializers.ValidationError(
                "This appointment already has a queue number."
            )

        return appointment

    @transaction.atomic
    def create(self, validated_data):

        queue_date = timezone.localdate()

        # Create or retrieve today's counter.
        QueueCounter.objects.get_or_create(
            queue_date=queue_date,
        )

        # Lock the counter to prevent duplicate numbers.
        counter = QueueCounter.objects.select_for_update().get(
            queue_date=queue_date,
        )

        number = counter.next_number

        # Q-20261118-0001
        queue_number = (
            f"Q-{queue_date:%Y%m%d}-{number:04d}"
        )

        counter.next_number += 1

        counter.save(
            update_fields=["next_number"]
        )

        return Queue.objects.create(
            **validated_data,
            queue_number=queue_number,
            queue_date=queue_date,
            status=QueueStatus.WAITING,
        )


class QueueStatusSerializer(serializers.ModelSerializer):

    status = serializers.ChoiceField(
        choices=QueueStatus.choices,
        required=True,
    )

    class Meta:
        model = Queue
        fields = ("status",)

    def validate_status(self, status):

        current_status = self.instance.status

        allowed_transitions = {
            QueueStatus.WAITING: (
                QueueStatus.SERVING,
                QueueStatus.SKIPPED,
            ),
            QueueStatus.SERVING: (
                QueueStatus.COMPLETED,
                QueueStatus.SKIPPED,
            ),
            QueueStatus.COMPLETED: (),
            QueueStatus.SKIPPED: (),
        }

        if status not in allowed_transitions[current_status]:
            raise serializers.ValidationError(
                f"Cannot transition queue from "
                f"{current_status} to {status}."
            )

        return status

    @transaction.atomic
    def update(self, instance, validated_data):

        status = validated_data["status"]
        now = timezone.now()

        instance.status = status

        if status == QueueStatus.SERVING:
            instance.called_at = now

        elif status == QueueStatus.COMPLETED:
            instance.completed_at = now

            appointment = instance.appointment
            if appointment.status != Appointment.Status.COMPLETED:
                appointment.status = Appointment.Status.COMPLETED
                appointment.save(update_fields=["status", "updated_at"])

        instance.save(
            update_fields=[
                "status",
                "called_at",
                "completed_at",
                "updated_at",
            ]
        )

        return instance
