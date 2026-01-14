# apps/authentication/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('refresh/', views.RefreshTokenView.as_view(), name='refresh-token'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('confirm-reset-password/', views.ConfirmResetPasswordView.as_view(), name='confirm-reset-password'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('profile/', views.ProfileView.as_view(), name='profile'),

    # Простой тестовый endpoint
    path('test/', views.TestView.as_view(), name='test-auth'),
]
