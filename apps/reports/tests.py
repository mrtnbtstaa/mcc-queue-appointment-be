from django.test import TestCase
from rest_framework.test import APITestCase

from apps.users.models import User, UserRole

from .services import ReportService


class ReportServiceTests(TestCase):

    def test_summary_pdf_is_a_pdf(self):
        pdf = ReportService.summary_pdf()

        self.assertTrue(pdf.startswith(b"%PDF"))


class SummaryReportViewTests(APITestCase):

    def setUp(self):
        self.student = User.objects.create_user(
            email="student@example.com",
            password="test-pass-123",
        )

    def test_only_staff_can_download(self):
        self.client.force_authenticate(self.student)

        response = self.client.get("/api/v1/reports/summary/")
        self.assertEqual(response.status_code, 403)

        self.student.role = UserRole.STAFF
        self.student.save(update_fields=["role"])

        response = self.client.get("/api/v1/reports/summary/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
