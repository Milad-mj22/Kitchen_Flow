# myapp/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('WA/<int:user_id>/', views.connect_whatsapp, name='connect_whatsapp'),
]