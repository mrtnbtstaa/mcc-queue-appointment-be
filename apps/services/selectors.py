from common.selectors.base import BaseSelector
from .models import DocumentService


class DocumentServiceSelector(BaseSelector):

    model = DocumentService

    searchable_fields = ("name", "category")

    ordering_fields = ("name", "fee", "created_at", "duration_min", "duration_max")

    default_ordering = ("name",)

    filterable_fields = {
        "name": ("exact", "icontains"),
        "category": ("exact",),
        "is_active": ("exact",),
        "fee": ("exact", "gte", "lte"),
        "duration_max": ("gte", "lte"),
        "created_at": ("date", "gte", "lte", "exact"),
        # Allows filtering by a specific document inside the JSON array:
        # e.g., GET /api/document-services/?required_documents=Student ID
        # "required_documents": ("contains",), 
    }