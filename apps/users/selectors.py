from common.selectors.base import BaseSelector
from .models import User

class UserSelector(BaseSelector):

    model = User

    searchable_fields = ("email", "name", "student_id")

    ordering_fields = ("email", "created_at")

    default_ordering = ("-created_at", )

    filterable_fields = {
        "created_at": (
            "date",
            "gte",
            "lte",
            "exact"
        ),
        "course": ("exact", ),
    }


