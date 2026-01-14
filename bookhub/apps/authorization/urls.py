# apps/authorization/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminRoleViewSet, AdminBusinessElementViewSet,
    AdminAccessRuleViewSet
)

router = DefaultRouter()
router.register(r'roles', AdminRoleViewSet, basename='admin-role')
router.register(r'elements', AdminBusinessElementViewSet, basename='admin-element')
router.register(r'permissions', AdminAccessRuleViewSet, basename='admin-permission')

urlpatterns = [
    path('', include(router.urls)),
]
