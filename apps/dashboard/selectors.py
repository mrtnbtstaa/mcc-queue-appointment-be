from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from apps.appointments.models import Appointment
from apps.queue_app.models import Queue, QueueStatus
from apps.services.models import DocumentService
from apps.transaction_record.models import Transaction


class DashboardSelector:
    """Read-only counters for the staff and student dashboards."""

    # ---------------------------------------------------------
    # Staff
    # ---------------------------------------------------------

    @classmethod
    def staff(cls) -> dict:

        today = timezone.localdate()
        yesterday = today - timedelta(days=1)

        today_appointments = Appointment.objects.filter(
            slot__appointment_date=today,
        )
        yesterday_total = Appointment.objects.filter(
            slot__appointment_date=yesterday,
        ).count()

        today_total = today_appointments.count()

        waiting = Queue.objects.filter(
            queue_date=today,
            status=QueueStatus.WAITING,
        )

        avg_wait = cls._average_wait(today)

        return {
            "role": "staff",
            "today_appointments": {
                "total": today_total,
                "confirmed": today_appointments.filter(
                    status=Appointment.Status.CONFIRMED,
                ).count(),
                "change_vs_yesterday": today_total - yesterday_total,
            },
            "waiting": {
                "students": waiting.count(),
                "avg_wait_minutes": avg_wait,
            },
            "now_serving": cls._now_serving(today),
            "completed_today": cls._completed_today(today),
        }

    # ---------------------------------------------------------
    # Student
    # ---------------------------------------------------------

    @classmethod
    def student(cls, user) -> dict:

        today = timezone.localdate()

        upcoming = Appointment.objects.filter(
            user=user,
            status__in=(
                Appointment.Status.PENDING,
                Appointment.Status.CONFIRMED,
            ),
            slot__appointment_date__gte=today,
        ).count()

        return {
            "role": "student",
            "upcoming_appointments": {"total": upcoming},
            "queue": cls._student_queue(user, today),
            "recent_records": {
                "total": Transaction.objects.filter(
                    appointment__user=user,
                ).count(),
            },
            "catalog": {
                "active_options": DocumentService.objects.filter(
                    is_active=True,
                ).count(),
            },
        }

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _average_wait(today) -> int:
        """Average minutes between queue creation and being called."""

        waits = Queue.objects.filter(
            queue_date=today,
            called_at__isnull=False,
        ).values_list("created_at", "called_at")

        minutes = [
            (called_at - created_at).total_seconds() / 60
            for created_at, called_at in waits
        ]

        return round(sum(minutes) / len(minutes)) if minutes else 0

    @staticmethod
    def _now_serving(today):

        queue = (
            Queue.objects.filter(
                queue_date=today,
                status=QueueStatus.SERVING,
            )
            .select_related("appointment__service")
            .order_by("called_at")
            .first()
        )

        if queue is None:
            return None

        return {
            "queue_number": queue.queue_number,
            "service_name": queue.appointment.service.name,
            "status": queue.status,
            "status_display": queue.get_status_display(),
        }

    @staticmethod
    def _completed_today(today) -> dict:

        transactions_today = Transaction.objects.filter(
            created_at__date=today,
        )
        completed = transactions_today.filter(
            transaction_status=Transaction.Status.COMPLETED,
        ).count()
        total = transactions_today.count()

        return {
            "transactions": completed,
            "completion_rate": round(completed / total * 100) if total else 0,
        }

    @staticmethod
    def _student_queue(user, today):

        queue = (
            Queue.objects.filter(
                appointment__user=user,
                queue_date=today,
                status__in=(
                    QueueStatus.WAITING,
                    QueueStatus.SERVING,
                ),
            )
            .select_related("appointment__service")
            .order_by("-created_at")
            .first()
        )

        if queue is None:
            return None

        return {
            "queue_number": queue.queue_number,
            "service_name": queue.appointment.service.name,
            "status": queue.status,
            "status_display": queue.get_status_display(),
            "position": (
                Queue.objects.filter(
                    queue_date=today,
                    status=QueueStatus.WAITING,
                    queue_number__lt=queue.queue_number,
                ).count()
                + 1
                if queue.status == QueueStatus.WAITING
                else 0
            ),
        }
