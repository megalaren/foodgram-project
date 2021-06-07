from django.urls import path

from . import views

urlpatterns = [
    path('password_change/',
         views.CustomPasswordChangeView.as_view(),
         name='password_change'),
    path('reset/<uidb64>/<token>/',
         views.CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('signup/',
         views.SignUp.as_view(),
         name='signup'),
]
