from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import RegistrationForm, MyAuthForm
from django.contrib.auth.views import LoginView
from custom_user.models import User
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags


class RegistrationView(View):
    template_name = 'register.html'

    def get(self, request, *args, **kwargs):
        form = RegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Puedes agregar lógica adicional aquí, como enviar un correo de confirmación.
            return redirect('login')  # Redirige al usuario a la página de inicio de sesión
        return render(request, self.template_name, {'form': form})
    
class MyLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = MyAuthForm

    def form_invalid(self, form):
        # Llama al método padre para obtener el comportamiento predeterminado
        response = super().form_invalid(form)
        # Agrega mensajes de error al contexto de la plantilla
        error_messages = form.errors['__all__'] if '__all__' in form.errors else None
        self.request.session['error_messages'] = error_messages
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Recupera mensajes de error del contexto de la sesión
        context['error_messages'] = self.request.session.pop('error_messages', None)
        return context   

def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff, login_url='login')
def user_admin_view(request):
    users = User.objects.all()

    return render(request, "users.html",{'users': users})

@user_passes_test(is_staff, login_url='login')
def order_review(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    
    review = order.review
    
    if review == None:
        raise Http404("El recurso no fue encontrado")

    if request.method == 'POST':
        new_status = request.POST.get('is_accepted')
        respuesta = request.POST.get('mensaje')
        email = order.email
        descripcion = review.description
        print(respuesta)
        if new_status in [Review.AcceptionStatus.ACCEPTED, Review.AcceptionStatus.DECLINED, Review.AcceptionStatus.PENDING]:
            review.is_accepted = new_status
            review.save()
            enviar_correo(request,respuesta, email, descripcion, new_status)

        else:
            return HttpResponseBadRequest("Estado de revisión no válido")
        
    return render(request, 'review.html', {'order':order,'review': review})

def enviar_correo(request, mensaje, email, descripcion, estado):
    subject = 'Gestión de Reclamación'
    message = render_to_string('email/gestionar_reclamacion.html', {'email':email, 'mensaje':mensaje, 'descripcion':descripcion, 'estado': estado})
    plain_message = strip_tags(message)
    from_email = 'phonedoctorpgpi@gmail.com' 
    to_email = [email] 

    send_mail(subject, plain_message, from_email, to_email, html_message=message)