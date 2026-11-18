from rest_framework.routers import DefaultRouter

from apps.transaction_record.views import TransactionViewSet


router = DefaultRouter()

router.register(r"transactions", TransactionViewSet, basename="transactions")