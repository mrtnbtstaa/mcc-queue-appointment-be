from datetime import time

from django.utils import timezone
from rest_framework.test import APITestCase

from apps.appointment_slot.models import AppointmentSlot
from apps.appointments.models import Appointment
from apps.queue_app.models import Queue, QueueStatus
from apps.services.models import DocumentService
from apps.transaction_record.models import Transaction
from apps.users.models import User, UserRole


class DashboardViewTests(APITestCase):

    def setUp(self):
        self.staff = User.objects.create_user(
            email="staff@example.com",
            password="test-pass-123",
            role=UserRole.STAFF,
        )
        self.student = User.objects.create_user(
            email="student@example.com",
            password="test-pass-123",
        )

        self.service = DocumentService.objects.create(
            name="Certificate of Enrollment",
        )
        self.slot = AppointmentSlot.objects.create(
            service=self.service,
            appointment_date=timezone.localdate(),
            start_time=time(9),
            end_time=time(10),
        )
        self.appointment = Appointment.objects.create(
            user=self.student,
            service=self.service,
            slot=self.slot,
            appointment_code="APT-TEST",
            status=Appointment.Status.CONFIRMED,
        )
        self.queue = Queue.objects.create(
            appointment=self.appointment,
            queue_number="Q-TEST-0001",
            queue_date=timezone.localdate(),
            status=QueueStatus.SERVING,
            called_at=timezone.now(),
        )
        Transaction.objects.create(
            appointment=self.appointment,
            processed_by=self.staff,
            transaction_status=Transaction.Status.COMPLETED,
            processed_at=timezone.now(),
        )

    def test_staff_counts(self):
        self.client.force_authenticate(self.staff)

        response = self.client.get("/api/v1/dashboard/")

        self.assertEqual(response.status_code, 200)

        data = response.data["data"]

        self.assertEqual(data["role"], "staff")
        self.assertEqual(data["today_appointments"]["total"], 1)
        self.assertEqual(data["today_appointments"]["confirmed"], 1)
        self.assertEqual(data["waiting"]["students"], 0)
        self.assertEqual(
            data["now_serving"]["queue_number"],
            self.queue.queue_number,
        )
        self.assertEqual(data["completed_today"]["transactions"], 1)
        self.assertEqual(data["completed_today"]["completion_rate"], 100)

    def test_student_counts(self):
        self.client.force_authenticate(self.student)

        response = self.client.get("/api/v1/dashboard/")

        self.assertEqual(response.status_code, 200)

        data = response.data["data"]

        self.assertEqual(data["role"], "student")
        self.assertEqual(data["upcoming_appointments"]["total"], 1)
        self.assertEqual(data["queue"]["queue_number"], self.queue.queue_number)
        self.assertEqual(data["recent_records"]["total"], 1)
        self.assertEqual(data["catalog"]["active_options"], 1)
