from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.appointments.models import Appointment
from apps.appointment_slot.models import AppointmentSlot
from apps.services.models import DocumentService
from apps.users.models import User

from .models import Queue, QueueStatus
from .serializers import QueueStatusSerializer


class QueueStatusCompletionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="student@example.com",
            password="password123",
            name="Student Name",
            student_id="2020-0001",
            course="bsit",
            year_level="1",
        )
        self.service = DocumentService.objects.create(name="TOR")
        self.slot = AppointmentSlot.objects.create(
            service=self.service,
            appointment_date=timezone.localdate() + timedelta(days=1),
            start_time="08:00:00",
            end_time="09:00:00",
            capacity=5,
        )
        self.appointment = Appointment.objects.create(
            user=self.user,
            service=self.service,
            slot=self.slot,
            appointment_code="APT-0001",
            status=Appointment.Status.CONFIRMED,
        )
        self.queue = Queue.objects.create(
            appointment=self.appointment,
            queue_number="Q-20261120-0001",
            queue_date=timezone.localdate(),
            status=QueueStatus.SERVING,
        )

    def _complete_queue(self):
        serializer = QueueStatusSerializer(
            self.queue,
            data={"status": QueueStatus.COMPLETED},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.queue.refresh_from_db()
        self.appointment.refresh_from_db()

    def test_completing_queue_completes_appointment(self):
        self._complete_queue()

        self.assertEqual(self.queue.status, QueueStatus.COMPLETED)
        self.assertIsNotNone(self.queue.completed_at)
        self.assertEqual(
            self.appointment.status,
            Appointment.Status.COMPLETED,
        )

    def test_other_queue_transitions_leave_appointment_status(self):
        serializer = QueueStatusSerializer(
            self.queue,
            data={"status": QueueStatus.SKIPPED},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.appointment.refresh_from_db()

        self.assertEqual(
            self.appointment.status,
            Appointment.Status.CONFIRMED,
        )
