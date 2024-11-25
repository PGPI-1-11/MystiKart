from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core.views import home
from django.contrib import admin 
from django.urls import path, include

urlpatterns = [
    path('', home,name='home'),
    path('admin/', admin.site.urls),
    path('product/', include('product.urls')),
    path('shoppingCart/', include('shoppingCart.urls')),  
    path('user/', include('custom_user.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
