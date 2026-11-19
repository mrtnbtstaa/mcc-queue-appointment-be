from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.services.models import DocumentService

from .models import AppointmentSlot
from .serializers import AppointmentSlotWriteSerializer


class AppointmentSlotWriteSerializerTests(TestCase):
    def setUp(self):
        self.service = DocumentService.objects.create(name="TOR")
        self.payload = {
            "service": "TOR",
            "appointment_date": timezone.localdate() + timedelta(days=1),
            "start_time": "08:00:00",
            "end_time": "09:00:00",
            "capacity": 5,
            "status": "AVAILABLE",
        }

    def test_service_resolves_by_name(self):
        serializer = AppointmentSlotWriteSerializer(data=self.payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["service"], self.service)

    def test_past_date_is_rejected(self):
        payload = {
            **self.payload,
            "appointment_date": timezone.localdate() - timedelta(days=1),
        }

        serializer = AppointmentSlotWriteSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("appointment_date", serializer.errors)

    def test_existing_past_slot_keeps_its_date(self):
        slot = AppointmentSlot.objects.create(
            service=self.service,
            appointment_date=timezone.localdate() - timedelta(days=1),
            start_time="08:00:00",
            end_time="09:00:00",
            capacity=5,
        )

        serializer = AppointmentSlotWriteSerializer(
            slot,
            data={
                "service": "TOR",
                "appointment_date": slot.appointment_date,
                "capacity": 6,
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
