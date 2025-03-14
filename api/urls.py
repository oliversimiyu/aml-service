from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, TransactionViewSet, DocumentVerificationViewSet
from .compliance_views import ComplianceViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'documents', DocumentVerificationViewSet)
router.register(r'compliance', ComplianceViewSet, basename='compliance')

urlpatterns = [
    path('', include(router.urls)),
]
