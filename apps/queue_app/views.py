
from django.db import transaction
from django.utils import timezone

from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied

from apps.notifications.models import NotificationCategory
from apps.notifications.services import NotificationService
from apps.users.models import UserRole
from common.views.api import ProtectedBaseAPiView
from common.views.viewsets import BaseModelViewSet
from common.responses.success import OkResponse

from .models import Queue
from .selectors import QueueSelector
from .serializers import (
    QueueListSerializer,
    QueueWriteSerializer,
    QueueStatusSerializer,
)


class QueueViewSet(
    BaseModelViewSet,
    ProtectedBaseAPiView,
):
    """Queue management endpoints."""

    selector = QueueSelector

    serializer_action_classes = {
        "list": QueueListSerializer,
        "retrieve": QueueListSerializer,
        "create": QueueWriteSerializer,
        "set_status": QueueStatusSerializer,
    }

    # Queue details are immutable after creation.
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT")

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PATCH")

    # ---- access ----------------------------------------------------------

    def _is_staff(self):
        user = self.request.user
        return user.role == UserRole.STAFF or user.is_staff

    def _require_staff(self):
        if not self._is_staff():
            raise PermissionDenied("Staff permission required.")

    def get_queryset(self):
        """Staff see every queue; students see today's live queue."""
        queryset = super().get_queryset()

        if self._is_staff():
            return queryset

        return queryset.filter(queue_date=timezone.localdate())

    def create(self, request, *args, **kwargs):
        self._require_staff()
        return super().create(request, *args, **kwargs)

    @action(
        detail=True,
        methods=["patch"],
        url_path="status",
    )
    @transaction.atomic
    def set_status(self, request, pk=None):
        """
        PATCH /api/v1/queues/{id}/status/

        Payload:
        {
            "status": "SERVING"
        }
        """

        self._require_staff()

        # Check object-level permissions first.
        instance = self.get_object()

        # Lock the queue to prevent concurrent status changes.
        instance = Queue.objects.select_for_update().get(
            pk=instance.pk
        )

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        NotificationService.notify_status_change(
            user=serializer.instance.appointment.user,
            category=NotificationCategory.QUEUE,
            reference_id=serializer.instance.pk,
            reference_label=f"Queue {serializer.instance.queue_number}",
            status_display=serializer.instance.get_status_display(),
        )

        return OkResponse(
            QueueListSerializer(
                serializer.instance,
                context=self.get_serializer_context(),
            ).data
        )
