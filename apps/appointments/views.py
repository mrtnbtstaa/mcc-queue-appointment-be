from django.db import transaction
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.appointment_slot.models import AppointmentSlot, Status
from apps.notifications.models import NotificationCategory
from apps.notifications.services import NotificationService
from apps.users.models import UserRole
from common.views.api import ProtectedBaseAPiView
from common.views.viewsets import BaseModelViewSet
from common.responses.success import OkResponse

from .selectors import AppointmentSelector
from .serializers import (
    AppointmentListSerializer,
    AppointmentWriteSerializer,
    AppointmentStatusSerializer,
)


class AppointmentViewSet(
    BaseModelViewSet,
    ProtectedBaseAPiView,
):
    """CRUD + status endpoint for student appointments."""

    selector = AppointmentSelector

    serializer_action_classes = {
        "list": AppointmentListSerializer,
        "retrieve": AppointmentListSerializer,
        "create": AppointmentWriteSerializer,
        "update": AppointmentWriteSerializer,
        "partial_update": AppointmentWriteSerializer,
        "set_status": AppointmentStatusSerializer,
    }

    # ---- hooks -----------------------------------------------------------

    def get_queryset(self):
        """Staff see every booking; students only see their own."""
        queryset = super().get_queryset()
        user = self.request.user

        if user.role == UserRole.STAFF or user.is_staff:
            return queryset

        return queryset.filter(user=user)

    def perform_create(self, serializer):
        """The student who books is always the authenticated user — never
        trust a ``user`` value coming from the request body."""
        with transaction.atomic():
            slot = AppointmentSlot.objects.select_for_update().get(
                pk=serializer.validated_data["slot"].pk
            )

            if slot.status not in (Status.AVAILABLE, "Open"):
                raise ValidationError(
                    {"slot": ["Selected slot is not available for booking."]}
                )

            if slot.remaining_capacity <= 0:
                raise ValidationError(
                    {"slot": ["Selected slot is already full."]}
                )

            serializer.validated_data["slot"] = slot
            serializer.save(user=self.request.user)

            if slot.remaining_capacity <= 0:
                slot.status = Status.FULL
                slot.save(update_fields=["status"])

    def perform_update(self, serializer):
        """Alert the student whenever their booking status changes."""
        previous_status = serializer.instance.status

        super().perform_update(serializer)

        if serializer.instance.status != previous_status:
            NotificationService.notify_status_change(
                user=serializer.instance.user,
                category=NotificationCategory.APPOINTMENT,
                reference_id=serializer.instance.pk,
                reference_label=serializer.instance.appointment_code,
                status_display=serializer.instance.get_status_display(),
            )

    # ---- custom actions --------------------------------------------------

    @action(
        detail=True,
        methods=["patch"],
        url_path="status",
    )
    def set_status(self, request, pk=None):
        """
        PATCH /api/appointments/{id}/status/

        Payload:
        {
            "status": "CONFIRMED"
        }

        Allowed transitions follow the model's Status enum, e.g.
        PENDING -> CONFIRMED -> COMPLETED  |  any -> CANCELLED.
        Additional business-rule checks (capacity, double-booking, ...)
        should be added in ``AppointmentStatusSerializer.validate_status``.
        """

        if request.user.role != UserRole.STAFF and not request.user.is_staff:
            raise PermissionDenied("Staff permission required.")

        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        return OkResponse(
            AppointmentListSerializer(instance).data,
        )