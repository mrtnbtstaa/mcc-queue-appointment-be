from datetime import date, datetime

from django.http import HttpResponse

from rest_framework.exceptions import PermissionDenied

from apps.users.models import UserRole
from common.exceptions.api import ValidationException
from common.views.api import ProtectedBaseAPiView

from .services import ReportService


class SummaryReportView(ProtectedBaseAPiView):
    """GET /api/v1/reports/summary/?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD

    Staff only. Always responds with a PDF file.
    """

    def get(self, request):
        user = request.user

        if user.role != UserRole.STAFF and not user.is_staff:
            raise PermissionDenied("Staff permission required.")

        date_from = self._parse_date(
            request.query_params.get("date_from"),
            "date_from",
        )
        date_to = self._parse_date(
            request.query_params.get("date_to"),
            "date_to",
        )

        if date_from and date_to and date_from > date_to:
            raise ValidationException(
                message="date_from must be before date_to.",
            )

        pdf = ReportService.summary_pdf(
            date_from=date_from,
            date_to=date_to,
        )

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="summary-report-{date.today():%Y%m%d}.pdf"'
        )

        return response

    @staticmethod
    def _parse_date(value: str | None, field: str):

        if not value:
            return None

        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationException(
                message=f"{field} must be in YYYY-MM-DD format.",
            )
