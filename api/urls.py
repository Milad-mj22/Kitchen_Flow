# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='api-home'),
    path('receive_sms/', views.receive_sms, name='receive_sms'),
    path('sms/', views.sms_page, name='sms_page'),
    path('load_messages/<int:count>/', views.get_last_sms, name='load_messages'),
]

