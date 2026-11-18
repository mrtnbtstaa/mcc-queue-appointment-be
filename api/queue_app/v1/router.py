from rest_framework.routers import DefaultRouter

from apps.queue_app.views import QueueViewSet


router = DefaultRouter()

router.register(r"queues", QueueViewSet, basename="queues")