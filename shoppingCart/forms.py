from django import forms
from .models import ShippingAddress

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['full_name', 'address', 'city', 'postal_code', 'country']
        labels = {  # Etiquetas en español
            'full_name': 'Nombre completo',
            'address': 'Dirección',
            'city': 'Ciudad',
            'postal_code': 'Código postal',
            'country': 'País',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Nombre completo'}),
            'address': forms.TextInput(attrs={'placeholder': 'Dirección'}),
            'city': forms.TextInput(attrs={'placeholder': 'Ciudad'}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'Código postal'}),
            'country': forms.TextInput(attrs={'placeholder': 'País'}),
        }
    full_name = forms.CharField(
        label="Nombre completo",
        error_messages={
            'required': 'Por favor, introduce tu nombre completo.',
        }
    )
    address = forms.CharField(
        label="Dirección",
        error_messages={
            'required': 'Por favor, proporciona tu dirección.',
        }
    )
    city = forms.CharField(
        label="Ciudad",
        error_messages={
            'required': 'Por favor, escribe la ciudad.',
        }
    )
    postal_code = forms.CharField(
        label="Código postal",
        error_messages={
            'required': 'Es necesario un código postal.',
        }
    )
    country = forms.CharField(
        label="País",
        error_messages={
            'required': 'Indica el país de envío.',
        }
    )
