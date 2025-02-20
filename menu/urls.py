from django.urls import path
from .views import set_sold_out, show_menu

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', show_menu, name='menu'),
    path('sold-out/', set_sold_out, name='set_sold_out'),
    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
