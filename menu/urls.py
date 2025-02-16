from django.urls import path
from .views import set_sold_out, show_menu

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', show_menu, name='users-home'),
    path('sold-out/', set_sold_out, name='set_sold_out'),
    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
