from django import forms
from .models import ShippingAddress

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['full_name', 'address', 'city', 'postal_code', 'country']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Nombre completo'}),
            'address': forms.TextInput(attrs={'placeholder': 'Dirección'}),
            'city': forms.TextInput(attrs={'placeholder': 'Ciudad'}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'Código postal'}),
            'country': forms.TextInput(attrs={'placeholder': 'País'}),
        }
