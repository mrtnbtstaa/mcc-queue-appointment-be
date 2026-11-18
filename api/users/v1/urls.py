from django.urls import include, path
from .router import router
from apps.users.views import FilterOptionsView

urlpatterns = [
    path("filters/", FilterOptionsView.as_view(), name="filter-options"),
    path("users/", include("apps.users.urls")),
    *router.urls
]