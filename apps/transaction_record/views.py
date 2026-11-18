from django.db import transaction as db_transaction
from django.utils import timezone

from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

from apps.notifications.models import NotificationCategory
from apps.notifications.services import NotificationService
from apps.users.models import UserRole
from common.views.api import ProtectedBaseAPiView
from common.views.viewsets import BaseModelViewSet
from common.responses.success import OkResponse

from .models import Transaction
from .selectors import TransactionSelector
from .serializers import (
    TransactionListSerializer,
    TransactionWriteSerializer,
    TransactionStatusSerializer,
)


class TransactionViewSet(
    BaseModelViewSet,
    ProtectedBaseAPiView,
):
    """CRUD + transaction status endpoint."""

    selector = TransactionSelector

    serializer_action_classes = {
        "list": TransactionListSerializer,
        "retrieve": TransactionListSerializer,
        "create": TransactionWriteSerializer,
        "update": TransactionWriteSerializer,
        "partial_update": TransactionWriteSerializer,
        "set_status": TransactionStatusSerializer,
    }

    # ---- hooks -----------------------------------------------------------

    def _is_staff(self):
        user = self.request.user
        return user.role == UserRole.STAFF or user.is_staff

    def _require_staff(self):
        if not self._is_staff():
            raise PermissionDenied("Staff permission required.")

    def get_queryset(self):
        """Staff see every transaction students only their own."""
        queryset = super().get_queryset()

        if self._is_staff():
            return queryset

        return queryset.filter(appointment__user=self.request.user)

    def create(self, request, *args, **kwargs):
        self._require_staff()
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self._require_staff()
        return super().update(request, *args, **kwargs)

    def perform_create(self, serializer):
        """The authenticated registrar is assigned automatically."""

        serializer.save(
            processed_by=self.request.user,
        )

    # ---- custom actions --------------------------------------------------

    @action(
        detail=True,
        methods=["patch"],
        url_path="status",
    )
    def set_status(self, request, pk=None):
        """
        PATCH /api/v1/transactions/{id}/status/

        Payload:
        {
            "transaction_status": "PROCESSING"
        }
        """

        self._require_staff()

        instance = self.get_object()

        with db_transaction.atomic():

            instance = Transaction.objects.select_for_update().get(
                pk=instance.pk,
            )

            serializer = TransactionStatusSerializer(
                instance,
                data=request.data,
                partial=True,
            )

            serializer.is_valid(raise_exception=True)

            new_status = serializer.validated_data[
                "transaction_status"
            ]

            update_fields = ["transaction_status", "updated_at", "remarks"]

            if new_status == Transaction.Status.PROCESSING:
                instance.processed_by = request.user
                instance.processed_at = timezone.now()

                update_fields.extend([
                    "processed_by",
                    "processed_at",
                ])

            instance.transaction_status = new_status
            instance.remarks = serializer.validated_data.get("remarks")


            instance.save(
                update_fields=update_fields,
            )

            NotificationService.notify_status_change(
                user=instance.appointment.user,
                category=NotificationCategory.TRANSACTION,
                reference_id=instance.pk,
                reference_label=(
                    f"Transaction {instance.appointment.appointment_code}"
                ),
                status_display=instance.get_transaction_status_display(),
            )

        return OkResponse(
            TransactionListSerializer(instance).data,
        )