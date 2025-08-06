from django.contrib.auth.forms import UserCreationForm
from django import forms
from newsletters.forms import StyleFormMixin
from users.models import User
from django.contrib.auth.forms import SetPasswordForm
from django.utils.translation import gettext_lazy as _


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']


class UserProfileForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'avatar', 'phone_number', 'country']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CustomSetPasswordForm(StyleFormMixin, SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].label = _('Новый пароль')
        self.fields['new_password2'].label = _('Подтверждение пароля')

        self.fields['new_password1'].help_text = None
        self.fields['new_password1'].widget.attrs.pop('aria-describedby', None)
        self.fields['new_password1'].widget.attrs.pop('data-toggle', None)
        self.fields['new_password1'].widget.attrs.pop('data-placement', None)

        self.fields['new_password1'].help_text = _(
            '<ul>'
            '<li>Ваш пароль не должен быть слишком похож на другую вашу личную информацию.</li>'
            '<li>Ваш пароль должен содержать не менее 8 символов.</li>'
            '<li>Ваш пароль не должен быть слишком простым.</li>'
            '<li>Ваш пароль не может состоять только из цифр.</li>'
            '</ul>'
        )