from rest_framework import serializers

from apps.services.models import DocumentService
from common.serializers.fields import RequiredCharField, RequiredDateField, RequiredIntegerField
from .models import AppointmentSlot, Status

class AppointmentSlotListSerializer(serializers.ModelSerializer):

    service_name = serializers.CharField(
        source="service.name",
        read_only=True,
    )

    # status_display = serializers.CharField(
    #     source="get_status_display",
    #     read_only=True,
    # )

    class Meta:
        model = AppointmentSlot
        fields = (
            "id",
            "service",
            "service_name",
            "appointment_date",
            "start_time",
            "end_time",
            "capacity",
            "status",
            # "status_display",
        )


class AppointmentSlotWriteSerializer(serializers.ModelSerializer):

    service = serializers.SlugRelatedField(
        slug_field="name",
        queryset=DocumentService.objects.all(),
        label="Service Name",
    )

    appointment_date = RequiredDateField(
        label="Appointment Date",
    )

    start_time = RequiredCharField(
        label="Start Time",
    )

    end_time = RequiredCharField(
        label="End Time",
    )

    capacity = RequiredIntegerField(
        label="Maximum Capacity",
        min_value=1,
    )

    status = serializers.ChoiceField(
        choices=Status.choices,
        label="Slot Status",
    )

    class Meta:
        model = AppointmentSlot
        fields = (
            "service",
            "appointment_date",
            "start_time",
            "end_time",
            "capacity",
            "status",
        )

    def validate(self, attrs):
        start_time = attrs.get(
            "start_time",
            getattr(self.instance, "start_time", None),
        )

        end_time = attrs.get(
            "end_time",
            getattr(self.instance, "end_time", None),
        )

        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError(
                {
                    "end_time": [
                        "End time must be later than start time."
                    ]
                }
            )

        return attrs

    def create(self, validated_data):
        return super().create(validated_data)



class AppointmentSlotStatusSerializer(serializers.ModelSerializer):

    status = serializers.ChoiceField(
        choices=Status.choices,
        required=True,
        label="Slot Status",
    )

    class Meta:
        model = AppointmentSlot
        fields = ("status",)