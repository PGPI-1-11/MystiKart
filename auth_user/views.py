from django.shortcuts import render, redirect
from django.views import View

from MystiKart.custom_user.models import User
from .forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import LoginView, CreateUserView

class RegistrationView(View):
    template_name = 'register.html'

    def get(self, request, *args, **kwargs):
        form = UserCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            print("Formulario válido, intentando guardar...")
            user = form.save()
            print("Usuario guardado exitosamente.")
            return redirect('login')
        else:
            print("Formulario no válido. Errores:", form.errors)
        return render(request, self.template_name, {'form': form})


class CustomLoginView(LoginView):
    form_class = AuthenticationForm

class CreateUserView(CreateUserView):
    form_class = UserCreationForm


