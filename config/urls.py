from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/", include("api.authentication.v1.urls")),
    path("api/v1/", include("api.users.v1.urls")),
    path("api/v1/", include("api.services.v1.urls")),
    path("api/v1/", include("api.appointment_slot.v1.urls")),
    path("api/v1/", include("api.appointments.v1.urls")),
    path("api/v1/", include("api.queue_app.v1.urls")),
    path("api/v1/", include("api.transaction_record.v1.urls")),
    path("api/v1/", include("api.notifications.v1.urls")),
    path("api/v1/", include("api.reports.v1.urls")),
    path("api/v1/", include("api.dashboard.v1.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
