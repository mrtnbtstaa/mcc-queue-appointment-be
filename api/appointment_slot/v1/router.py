from rest_framework.routers import DefaultRouter

from apps.appointment_slot.views import AppointmentSlotViewSet


router = DefaultRouter()

router.register(r"appointment-slots", AppointmentSlotViewSet, basename="appointment-slots")