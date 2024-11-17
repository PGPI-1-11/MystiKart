from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from auth_user.views import RegistrationView
from core import views
from django.contrib import admin 
from django.urls import path, include

urlpatterns = [
    path('', views.home,name='home'),
    path('admin/', admin.site.urls),
    path('register/', RegistrationView.as_view(), name='register'),

]