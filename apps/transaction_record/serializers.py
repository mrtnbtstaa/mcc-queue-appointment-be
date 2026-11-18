from django.utils import timezone
from rest_framework import serializers

from apps.appointments.models import Appointment
from apps.queue_app.models import Queue
from common.serializers.fields import RequiredCharField

from .models import Transaction


class TransactionListSerializer(serializers.ModelSerializer):

    appointment_code = serializers.CharField(
        source="appointment.appointment_code",
        read_only=True,
    )

    student_name = serializers.CharField(
        source="appointment.user.name",
        read_only=True,
        allow_null=True,
    )

    student_id = serializers.CharField(
        source="appointment.user.student_id",
        read_only=True,
        allow_null=True,
    )

    course = serializers.CharField(
        source="appointment.user.course",
        read_only=True,
        allow_null=True,
    )

    year_level = serializers.CharField(
        source="appointment.user.year_level",
        read_only=True,
        allow_null=True,
    )

    service_name = serializers.CharField(
        source="appointment.service.name",
        read_only=True,
    )

    slot_schedule = serializers.CharField(
        source="appointment.slot.slot_schedule",
        read_only=True,
    )

    queue_number = serializers.SerializerMethodField()

    processed_by_name = serializers.CharField(
        source="processed_by.name",
        read_only=True,
        allow_null=True,
    )

    transaction_status_display = serializers.CharField(
        source="get_transaction_status_display",
        read_only=True,
    )

    class Meta:
        model = Transaction
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
            "processed_by",
            "processed_by_name",
            "transaction_status",
            "transaction_status_display",
            "remarks",
            "processed_at",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_queue_number(self, obj):
        try:
            return obj.appointment.queue.queue_number
        except Queue.DoesNotExist:
            return ""


class TransactionWriteSerializer(serializers.ModelSerializer):

    appointment = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all(),
        label="Appointment",
    )

    remarks = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    class Meta:
        model = Transaction
        fields = (
            "appointment",
            "remarks",
        )

    def validate_appointment(self, appointment):

        # Prevent changing the associated appointment after creation.
        if (
            self.instance
            and self.instance.appointment_id != appointment.pk
        ):
            raise serializers.ValidationError(
                "The associated appointment cannot be changed."
            )

        return appointment

    def validate(self, attrs):

        # Add appointment-specific business rules here if necessary.
        return attrs


class TransactionStatusSerializer(serializers.ModelSerializer):

    transaction_status = serializers.ChoiceField(
        choices=Transaction.Status.choices,
        required=True,
        label="Transaction Status",
    )

    remarks = serializers.CharField(
        allow_null=True,
        allow_blank=True
    )

    class Meta:
        model = Transaction
        fields = ("transaction_status", "remarks")

    def validate_transaction_status(self, new_status):

        current_status = self.instance.transaction_status

        allowed_transitions = {
            Transaction.Status.PENDING: (
                Transaction.Status.PROCESSING,
                Transaction.Status.CANCELLED,
            ),
            Transaction.Status.PROCESSING: (
                Transaction.Status.COMPLETED,
                Transaction.Status.CANCELLED,
            ),
            Transaction.Status.COMPLETED: (),
            Transaction.Status.CANCELLED: (),
        }

        if new_status == current_status:
            raise serializers.ValidationError(
                "Transaction already has this status."
            )

        if new_status not in allowed_transitions[current_status]:
            raise serializers.ValidationError(
                f"Cannot change transaction status from "
                f"{current_status} to {new_status}."
            )

        return new_status