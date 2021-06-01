from django.contrib.auth.views import (PasswordChangeView,
                                       PasswordResetConfirmView)
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import (CreationForm, CustomPasswordChangeForm,
                    CustomSetPasswordForm)


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
