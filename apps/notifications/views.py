from django.utils import timezone

from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed

from common.constants.messages import Messages
from common.responses.success import OkResponse
from common.views.api import ProtectedBaseAPiView
from common.views.viewsets import BaseModelViewSet

from .selectors import NotificationSelector
from .serializers import NotificationSerializer


class NotificationViewSet(
    BaseModelViewSet,
    ProtectedBaseAPiView,
):
    """Read-only inbox for the authenticated user's alerts.

    Alerts are created by ``NotificationService`` when a record's
    status changes; clients poll ``unread-count`` for live badge data.
    """

    selector = NotificationSelector

    serializer_action_classes = {
        "list": NotificationSerializer,
        "retrieve": NotificationSerializer,
    }

    # ---- access ----------------------------------------------------------

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    # Alerts are system-generated; no direct writes.

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed("POST")

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT")

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed("DELETE")

    # ---- custom actions --------------------------------------------------

    @action(
        detail=True,
        methods=["post"],
        url_path="read",
    )
    def mark_read(self, request, pk=None):
        instance = self.get_object()

        if not instance.is_read:
            instance.is_read = True
            instance.save(update_fields=["is_read", "updated_at"])

        return OkResponse(
            NotificationSerializer(instance).data,
            message=Messages.UPDATED,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="read-all",
    )
    def mark_all_read(self, request):
        updated = (
            self.get_queryset()
            .filter(is_read=False)
            .update(is_read=True, updated_at=timezone.now())
        )

        return OkResponse(
            {"updated": updated},
            message=Messages.UPDATED,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="unread-count",
    )
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()

        return OkResponse({"unread": count})
