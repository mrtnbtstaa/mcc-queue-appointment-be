from rest_framework.decorators import action

from common.views.api import ProtectedBaseAPiView
from common.views.viewsets import BaseModelViewSet
from common.responses.success import OkResponse

from .selectors import DocumentServiceSelector
from .serializers import (
    DocumentServiceListSerializer,
    DocumentServiceWriteSerializer,
    DocumentServiceStatusSerializer, 
)

class DocumentServiceViewSet(BaseModelViewSet, ProtectedBaseAPiView):

    selector = DocumentServiceSelector

    serializer_action_classes = {
        "list": DocumentServiceListSerializer,
        "retrieve": DocumentServiceListSerializer,
        "create": DocumentServiceWriteSerializer,
        "update": DocumentServiceWriteSerializer,
        "partial_update": DocumentServiceWriteSerializer,
        "set_status": DocumentServiceStatusSerializer, 
    }

    @action(detail=True, methods=["patch"], url_path="status")
    def set_status(self, request, pk=None):
        """
        Custom action to explicitly activate or deactivate a service.
        Endpoint: PATCH /api/document-services/{id}/status/
        Payload: {"is_active": true}
        """
        # 1. Get the instance (leveraging BaseModelViewSet's get_object)
        instance = self.get_object()
        
        # 2. Validate input using the mapped serializer
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # 3. Save and return response
        self.perform_update(serializer)
        
        # Return the List Serializer so the frontend gets the fully updated object
        # (including computed fields like fee_display, required_documents, etc.)
        return OkResponse(
            DocumentServiceListSerializer(instance).data, 
        )