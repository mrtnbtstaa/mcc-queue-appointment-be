from __future__ import annotations

from django.db.models import Count
from django.utils import timezone

from apps.appointments.models import Appointment
from apps.transaction_record.models import Transaction


class ReportSelector:
    """Aggregates appointment and transaction records for reporting."""

    @staticmethod
    def summary(
        *,
        date_from=None,
        date_to=None,
    ) -> dict:

        appointments = Appointment.objects.all()
        transactions = Transaction.objects.all()

        if date_from:
            appointments = appointments.filter(
                created_at__date__gte=date_from,
            )
            transactions = transactions.filter(
                created_at__date__gte=date_from,
            )

        if date_to:
            appointments = appointments.filter(
                created_at__date__lte=date_to,
            )
            transactions = transactions.filter(
                created_at__date__lte=date_to,
            )

        return {
            "generated_at": timezone.localtime(),
            "date_from": date_from,
            "date_to": date_to,
            "appointment_total": appointments.count(),
            "transaction_total": transactions.count(),
            "appointment_statuses": ReportSelector._status_breakdown(
                appointments,
                "status",
                Appointment.Status.choices,
            ),
            "transaction_statuses": ReportSelector._status_breakdown(
                transactions,
                "transaction_status",
                Transaction.Status.choices,
            ),
        }

    @staticmethod
    def _status_breakdown(
        queryset,
        field: str,
        choices,
    ) -> list[dict]:

        counts = {
            row[field]: row["count"]
            for row in queryset.values(field).annotate(count=Count("id"))
        }

        return [
            {
                "status": label,
                "count": counts.get(value, 0),
            }
            for value, label in choices
        ]
