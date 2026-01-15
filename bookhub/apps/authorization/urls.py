from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdminAccessRuleViewSet, AdminBusinessElementViewSet, AdminRoleViewSet

router = DefaultRouter()
router.register(r"roles", AdminRoleViewSet, basename="admin-role")
router.register(r"elements", AdminBusinessElementViewSet, basename="admin-element")
router.register(r"permissions", AdminAccessRuleViewSet, basename="admin-permission")

urlpatterns = [
    path("", include(router.urls)),
]
