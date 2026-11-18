from django.urls import path

from apps.reports.views import SummaryReportView

urlpatterns = [
    path(
        "reports/summary/",
        SummaryReportView.as_view(),
        name="summary-report",
    ),
]
