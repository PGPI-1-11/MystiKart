# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.generic.edit import FormView
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=100, help_text='Required. Enter a valid email address.', label=_("Correo electrónico"))
    password1 = forms.CharField(
        label=_("Contraseña"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Confirmar Contraseña"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Personalizar mensajes de error
        self.fields['password1'].widget.attrs['autocomplete'] = 'new-password'  # Evitar autocompletar en algunos navegadores
        self.fields['password1'].error_messages = {
            'password_too_short': _('La contraseña debe tener al menos 8 caracteres.'),
            'password_too_common': _('La contraseña es demasiado común.'),
            'password_entirely_numeric': _('La contraseña no puede ser completamente numérica.'),
        }
        
        self.fields['password2'].widget.attrs['autocomplete'] = 'new-password'  # Evitar autocompletar en algunos navegadores
        self.fields['password2'].error_messages = {
            'password_mismatch': _("Las contraseñas no coinciden."),
        }

        self.fields['email'].error_messages = {
            'unique': _('Este correo electrónico ya está registrado.'),
        }


    def clean_password2(self):
        pass1=self.cleaned_data['password1']
        pass2=self.cleaned_data['password2']

        if pass1 != pass2:
            raise ValidationError(_('Las contraseñas no coinciden'))
        
        if pass1.isdigit():
            raise ValidationError(_('La contraseña no puede ser completamente numérica'))
        
        if len(pass1) < 8:
            raise ValidationError(_('La contraseña debe tener al menos 8 caracteres'))
        
        return pass2
class MyAuthForm(AuthenticationForm):
    error_messages = {
        'invalid_login': _(
            "Por favor, introduzca un email y contraeña correctos"
        ),
        'inactive': _("La cuenta está inactiva"),
    }