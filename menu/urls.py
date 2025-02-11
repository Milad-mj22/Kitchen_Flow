from django.urls import path
from .views import show_menu

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', show_menu, name='users-home'),
    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
