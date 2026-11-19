from common.responses.success import OkResponse
from common.email.service import EmailService
from common.constants.messages import Messages
from common.views.viewsets import BaseModelViewSet
from common.views.api import ProtectedBaseAPiView, PublicBaseApiView
from apps.appointments.models import Appointment
from apps.queue_app.models import QueueStatus
from apps.services.models import ServiceCategory
from .models import Course
from .selectors import UserSelector
from .serializers import UserSerializer, UserUpdateProfileSerializer


class FilterOptionsView(PublicBaseApiView):
    """GET /api/v1/filters/

    Option lists consumed by the frontend filter controls.
    """

    def get(self, request):
        return OkResponse(
            {
                "courses": [
                    {"value": value, "label": label}
                    for value, label in Course.choices
                ],
                "service_categories": [
                    {"value": value, "label": label}
                    for value, label in ServiceCategory.choices
                ],
                "appointment_statuses": [
                    {"value": value, "label": label}
                    for value, label in Appointment.Status.choices
                ],
                "queue_statuses": [
                    {"value": value, "label": label}
                    for value, label in QueueStatus.choices
                ],
            }
        )

class ResendEmailVerificationView(ProtectedBaseAPiView):

    def get(self, request):

        self.check_throttles(request)

        _ = EmailService.resend_email_verification(request.user)

        return OkResponse(message=Messages.EMAIL_LINK_SENT)


class UsersViewSet(BaseModelViewSet, ProtectedBaseAPiView):

    selector = UserSelector

    serializer_action_classes = {
        "list": UserSerializer,
        "retrieve": UserSerializer,
        "update": UserUpdateProfileSerializer
    }

    