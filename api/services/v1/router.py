from rest_framework.routers import DefaultRouter

from apps.services.views import DocumentServiceViewSet

router = DefaultRouter()

router.register(r"document-services", DocumentServiceViewSet, basename="document-services")