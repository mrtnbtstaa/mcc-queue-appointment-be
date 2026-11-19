from django.test import TestCase
from rest_framework.test import APIClient

from .models import User, UserRole


class UserUpdateTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            email="staff@example.com",
            password="password123",
            role=UserRole.STAFF,
            is_staff=True,
        )
        self.student = User.objects.create_user(
            email="student@example.com",
            password="password123",
            name="Student Name",
            student_id="2020-0001",
            course="bsit",
            year_level="1",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.staff)

    def _patch(self, payload):
        return self.client.patch(
            f"/api/v1/users/{self.student.id}/",
            payload,
            format="json",
        )

    def test_partial_update_saves_all_fields(self):
        response = self._patch(
            {
                "name": "Updated Name",
                "student_id": "2020-0002",
                "email": "updated@example.com",
                "course": "bsma",
                "year_level": "2",
                "is_active": False,
            }
        )

        self.assertEqual(response.status_code, 200, response.content)

        self.student.refresh_from_db()
        self.assertEqual(self.student.name, "Updated Name")
        self.assertEqual(self.student.student_id, "2020-0002")
        self.assertEqual(self.student.email, "updated@example.com")
        self.assertEqual(self.student.course, "bsma")
        self.assertEqual(self.student.year_level, "2")
        self.assertFalse(self.student.is_active)

    def test_partial_update_accepts_a_single_field(self):
        response = self._patch({"year_level": "3"})

        self.assertEqual(response.status_code, 200, response.content)

        self.student.refresh_from_db()
        self.assertEqual(self.student.year_level, "3")
        self.assertEqual(self.student.name, "Student Name")

    def test_duplicate_student_id_is_rejected(self):
        User.objects.create_user(
            email="other@example.com",
            password="password123",
            name="Other Student",
            student_id="2020-9999",
            course="bsit",
            year_level="1",
        )

        response = self._patch({"student_id": "2020-9999"})

        self.assertEqual(response.status_code, 400, response.content)
        self.assertIn("student_id", response.json()["errors"])

    def test_invalid_course_is_rejected(self):
        response = self._patch({"course": "not-a-course"})

        self.assertEqual(response.status_code, 400, response.content)
        self.assertIn("course", response.json()["errors"])
