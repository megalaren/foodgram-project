from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


from django.contrib.auth import password_validation


class CreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = (
            'Ваш пароль не должен совпадать с вашим именем или другой '
            'персональной информацией или быть слишком похожим на неё.\n'
            'Ваш пароль должен содержать как минимум 8 символов.\n'
            'Ваш пароль не может быть одним из широко распространённых '
            'паролей.\n'
            'Ваш пароль не может состоять только из цифр.'
        )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
