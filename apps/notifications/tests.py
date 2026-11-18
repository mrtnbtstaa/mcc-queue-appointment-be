from datetime import date, time

from rest_framework.test import APITestCase

from apps.appointment_slot.models import AppointmentSlot
from apps.appointments.models import Appointment
from apps.services.models import DocumentService
from apps.users.models import User, UserRole

from .models import Notification, NotificationCategory


class NotificationViewSetTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="student@example.com",
            password="test-pass-123",
        )
        self.other = User.objects.create_user(
            email="other@example.com",
            password="test-pass-123",
        )
        self.client.force_authenticate(self.user)

    def test_inbox_is_scoped_and_mark_read(self):
        own = Notification.objects.create(
            user=self.user,
            category=NotificationCategory.APPOINTMENT,
            title="Appointment status updated",
            message="APT-1 is now Confirmed.",
        )
        Notification.objects.create(
            user=self.other,
            category=NotificationCategory.QUEUE,
            title="Queue status updated",
            message="Q-1 is now Serving.",
        )

        response = self.client.get("/api/v1/notifications/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["data"]), 1)

        response = self.client.get("/api/v1/notifications/unread-count/")
        self.assertEqual(response.data["data"]["unread"], 1)

        response = self.client.post(f"/api/v1/notifications/{own.pk}/read/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["data"]["is_read"])

        response = self.client.get("/api/v1/notifications/unread-count/")
        self.assertEqual(response.data["data"]["unread"], 0)

    def test_appointment_status_change_creates_alert(self):
        staff = User.objects.create_user(
            email="staff@example.com",
            password="test-pass-123",
            role=UserRole.STAFF,
        )
        service = DocumentService.objects.create(
            name="Certificate of Enrollment",
        )
        slot = AppointmentSlot.objects.create(
            service=service,
            appointment_date=date.today(),
            start_time=time(9),
            end_time=time(10),
        )
        appointment = Appointment.objects.create(
            user=self.user,
            service=service,
            slot=slot,
            appointment_code="APT-TEST",
        )

        self.client.force_authenticate(staff)

        response = self.client.patch(
            f"/api/v1/appointments/{appointment.pk}/status/",
            {"status": Appointment.Status.CONFIRMED},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Notification.objects.filter(
                user=self.user,
                category=NotificationCategory.APPOINTMENT,
                reference_id=appointment.pk,
            ).exists()
        )
