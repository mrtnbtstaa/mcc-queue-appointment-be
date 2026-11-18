from apps.users.models import UserRole
from common.responses.success import OkResponse
from common.views.api import ProtectedBaseAPiView

from .selectors import DashboardSelector


class DashboardView(ProtectedBaseAPiView):
    """GET /api/v1/dashboard/

    Returns the counter payload for the caller's role.
    """

    def get(self, request):
        user = request.user

        if user.role == UserRole.STAFF or user.is_staff:
            data = DashboardSelector.staff()
        else:
            data = DashboardSelector.student(user)

        return OkResponse(data)
