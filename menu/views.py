from django.shortcuts import render
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib.auth import logout

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.contrib.auth.decorators import login_required
from khayyam import JalaliDatetime
# Create your views here.

from users.models import mother_food , FoodRawMaterial


@login_required
def show_menu(request):
        
            # mother_foods = mother_food.objects.all()
            # foods = FoodRawMaterial.objects.all()

            # food_names = list(FoodRawMaterial.objects.values_list('name', flat=True))
            pizza_single = FoodRawMaterial.objects.filter(mother__name='پیتزا تکنفره')
            pizza_double = FoodRawMaterial.objects.filter(mother__name='پیتزا دونفره')



            return render(request, 'users/menu.html',{'pizza_single':pizza_single,'pizza_double':pizza_double})

