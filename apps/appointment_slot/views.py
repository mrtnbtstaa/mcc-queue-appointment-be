from rest_framework.decorators import action

from common.views.api import ProtectedBaseAPiView
from common.views.viewsets import BaseModelViewSet
from common.responses.success import OkResponse

from .selectors import AppointmentSlotSelector
from .serializers import (
    AppointmentSlotListSerializer,
    AppointmentSlotWriteSerializer,
    AppointmentSlotStatusSerializer,
)


class AppointmentSlotViewSet(
    BaseModelViewSet,
    ProtectedBaseAPiView,
):

    selector = AppointmentSlotSelector

    serializer_action_classes = {
        "list": AppointmentSlotListSerializer,
        "retrieve": AppointmentSlotListSerializer,
        "create": AppointmentSlotWriteSerializer,
        "update": AppointmentSlotWriteSerializer,
        "partial_update": AppointmentSlotWriteSerializer,
        "set_status": AppointmentSlotStatusSerializer,
    }

    @action(
        detail=True,
        methods=["patch"],
        url_path="status",
    )
    def set_status(self, request, pk=None):
        """
        PATCH /api/appointment-slots/{id}/status/

        Payload:
        {
            "status": "AVAILABLE"
        }
        """

        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        return OkResponse(
            AppointmentSlotListSerializer(instance).data,
        )